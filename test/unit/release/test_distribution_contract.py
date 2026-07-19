from __future__ import annotations

import gzip
import io
import tarfile
import tomllib
import zipfile
from pathlib import Path

import pytest

from scripts.release.distribution import (
    DistributionContractError,
    check_distribution_directory,
    normalize_sdist,
    sha256_file,
)

ROOT = Path(__file__).parents[3]
PROJECT_VERSION = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
    "project"
]["version"]
DIST_INFO = f"forml-{PROJECT_VERSION}.dist-info"
SDIST_ROOT = f"forml-{PROJECT_VERSION}"

WHEEL_MEMBERS = {
    "forml/__init__.py": b"from dsl.runtime import verify\n",
    "dsl/__init__.py": b"",
    "model/__init__.py": b"",
    "dsl/language/grammar/forml_grammar.ebnf": b"start = program\n",
    "dsl/language/grammar/forml_grammar.lark": b"start: program\n",
    f"{DIST_INFO}/METADATA": (
        f"Metadata-Version: 2.1\nName: forml\nVersion: {PROJECT_VERSION}\n\n".encode()
    ),
    f"{DIST_INFO}/WHEEL": b"Wheel-Version: 1.0\nTag: py3-none-any\n",
    f"{DIST_INFO}/RECORD": b"",
}


def _write_wheel(path: Path, *, leak_tests: bool = False) -> None:
    with zipfile.ZipFile(path, mode="w") as archive:
        for name, payload in WHEEL_MEMBERS.items():
            archive.writestr(name, payload)
        if leak_tests:
            archive.writestr("test/test_leak.py", b"")


def _write_sdist(path: Path, *, mtime: int) -> None:
    members = {
        f"{SDIST_ROOT}/LICENSE": b"license\n",
        f"{SDIST_ROOT}/README.md": b"readme\n",
        f"{SDIST_ROOT}/CHANGELOG.md": b"changelog\n",
        f"{SDIST_ROOT}/pyproject.toml": (
            f"[project]\nname='forml'\nversion='{PROJECT_VERSION}'\n".encode()
        ),
        f"{SDIST_ROOT}/forml/__init__.py": b"",
        f"{SDIST_ROOT}/dsl/__init__.py": b"",
        f"{SDIST_ROOT}/model/__init__.py": b"",
        f"{SDIST_ROOT}/dsl/language/grammar/forml_grammar.ebnf": b"start=program\n",
        f"{SDIST_ROOT}/dsl/language/grammar/forml_grammar.lark": b"start: program\n",
    }
    with path.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", mtime=mtime) as compressed:
            with tarfile.open(fileobj=compressed, mode="w") as archive:
                for name, payload in members.items():
                    info = tarfile.TarInfo(name)
                    info.size = len(payload)
                    info.mtime = mtime
                    archive.addfile(info, io.BytesIO(payload))


def test_distribution_contract_accepts_complete_wheel_and_sdist(
    tmp_path: Path,
) -> None:
    _write_wheel(tmp_path / f"forml-{PROJECT_VERSION}-py3-none-any.whl")
    _write_sdist(tmp_path / f"forml-{PROJECT_VERSION}.tar.gz", mtime=100)

    artifacts = check_distribution_directory(tmp_path)

    assert artifacts.wheel.name.endswith(".whl")
    assert artifacts.sdist.name.endswith(".tar.gz")


def test_distribution_contract_rejects_repository_paths_in_wheel(
    tmp_path: Path,
) -> None:
    _write_wheel(
        tmp_path / f"forml-{PROJECT_VERSION}-py3-none-any.whl",
        leak_tests=True,
    )
    _write_sdist(tmp_path / f"forml-{PROJECT_VERSION}.tar.gz", mtime=100)

    with pytest.raises(DistributionContractError, match="repository-only"):
        check_distribution_directory(tmp_path)


def test_sdist_normalization_removes_timestamp_differences(tmp_path: Path) -> None:
    first = tmp_path / "first.tar.gz"
    second = tmp_path / "second.tar.gz"
    _write_sdist(first, mtime=100)
    _write_sdist(second, mtime=200)

    normalize_sdist(first, epoch=1_700_000_000)
    normalize_sdist(second, epoch=1_700_000_000)

    assert sha256_file(first) == sha256_file(second)
