from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from scripts.release.check_installed_distribution import (
    check_installed_origin,
    check_installed_typing,
)
from scripts.release import check_installed_distribution as installed


@pytest.mark.parametrize(
    ("score", "local_sources", "message"),
    (
        (0.5, False, "type completeness failed"),
        (1.0, True, "outside the clean venv"),
    ),
)
def test_installed_typing_rejects_incomplete_types_or_local_source_fallback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    score: float,
    local_sources: bool,
    message: str,
) -> None:
    python = tmp_path / "venv" / "bin" / "python"
    package = (
        tmp_path / "source" / "toetra"
        if local_sources
        else tmp_path / "venv" / "lib" / "site-packages" / "toetra"
    )
    result = {
        "typeCompleteness": {
            "packageRootDirectory": str(package),
            "completenessScore": score,
            "symbols": [],
        }
    }

    def run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        # A zero exit status alone does not imply complete exported types.
        return subprocess.CompletedProcess(command, 0, stdout=json.dumps(result))

    monkeypatch.setattr(
        "scripts.release.check_installed_distribution.subprocess.run", run
    )
    with pytest.raises(RuntimeError, match=message):
        check_installed_typing(python, tmp_path, environment={})


@pytest.mark.parametrize("location", ("checkout", "other-venv"))
def test_import_probe_rejects_sources_or_a_different_installation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, location: str
) -> None:
    python = tmp_path / "venv" / "bin" / "python"
    module = (
        tmp_path / "src" / "toetra" / "__init__.py"
        if location == "checkout"
        else tmp_path / "other-venv" / "site-packages" / "toetra" / "__init__.py"
    )

    def run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 0, stdout=str(module))

    monkeypatch.setattr(installed.subprocess, "run", run)
    with pytest.raises(
        RuntimeError, match="Import resolved Toetra outside the clean venv"
    ):
        check_installed_origin(python, tmp_path, environment={})


@pytest.mark.parametrize(
    ("arguments", "formats"),
    (
        ([], ("wheel",)),
        (["--format", "sdist"], ("sdist",)),
        (["--format", "both"], ("wheel", "sdist")),
    ),
)
def test_installation_entry_point_dispatches_formats_to_the_same_journey(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    arguments: list[str],
    formats: tuple[str, ...],
) -> None:
    observed: list[Path] = []
    archives = tuple(tmp_path / format for format in formats)

    def select(directory: Path, *, format: str, repository: Path) -> tuple[Path, ...]:
        assert format == ("both" if len(formats) == 2 else formats[0])
        return archives

    def check(
        archive: Path, *, repository_root: Path, pyright_requirement: str
    ) -> None:
        observed.append(archive)

    monkeypatch.setattr(installed, "installation_artifacts", select)
    monkeypatch.setattr(installed, "check_installed_archive", check)

    assert installed.main(arguments) == 0
    assert tuple(observed) == archives
