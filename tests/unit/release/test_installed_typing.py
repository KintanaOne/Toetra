from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from scripts.release.check_installed_distribution import check_installed_typing


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
