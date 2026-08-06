from __future__ import annotations

import os
from pathlib import Path

import pytest

from scripts.ci.check_cli_smoke import (
    CliSmokeError,
    console_for_python,
    project_version,
)


def test_project_version_reads_the_pep_621_project_table(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "toetra"\nversion = "1.2.3rc4"\n',
        encoding="utf-8",
    )

    assert project_version(tmp_path) == "1.2.3rc4"


def test_project_version_rejects_missing_version(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "toetra"\n',
        encoding="utf-8",
    )

    with pytest.raises(CliSmokeError, match="does not declare a project version"):
        project_version(tmp_path)


def test_console_for_python_uses_the_active_environment_directory(
    tmp_path: Path,
) -> None:
    executable_directory = tmp_path / ("Scripts" if os.name == "nt" else "bin")
    executable_directory.mkdir()
    python = executable_directory / ("python.exe" if os.name == "nt" else "python")
    console = executable_directory / ("toetra.exe" if os.name == "nt" else "toetra")
    python.write_text("", encoding="utf-8")
    console.write_text("", encoding="utf-8")

    assert console_for_python(python) == console.resolve()


def test_console_for_python_rejects_missing_entry_point(tmp_path: Path) -> None:
    python = tmp_path / ("python.exe" if os.name == "nt" else "python")
    python.write_text("", encoding="utf-8")

    with pytest.raises(CliSmokeError, match="console script not found"):
        console_for_python(python)


@pytest.mark.skipif(
    os.name == "nt",
    reason="virtualenv Python symlinks are POSIX-specific",
)
def test_console_for_python_does_not_dereference_virtualenv_symlink(
    tmp_path: Path,
) -> None:
    system = tmp_path / "system"
    environment = tmp_path / "environment" / "bin"
    system.mkdir()
    environment.mkdir(parents=True)
    real_python = system / "python"
    real_python.write_text("", encoding="utf-8")
    python = environment / "python"
    python.symlink_to(real_python)
    console = environment / "toetra"
    console.write_text("", encoding="utf-8")

    assert console_for_python(python) == console
