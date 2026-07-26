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
    ensure_clean_repository,
    normalize_sdist,
    sha256_file,
)

ROOT = Path(__file__).parents[3]
PROJECT_VERSION = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
    "project"
]["version"]
DIST_INFO = f"toetra-{PROJECT_VERSION}.dist-info"
SDIST_ROOT = f"toetra-{PROJECT_VERSION}"

WHEEL_MEMBERS = {
    "toetra/__init__.py": b"from toetra._runtime import verify\n",
    "toetra/_language/grammar/toetra_grammar.ebnf": b"start = program\n",
    "toetra/_language/grammar/toetra_grammar.lark": b"start: program\n",
    "toetra/examples/credit_risk_policy.toetra": b"target := risk_score\n",
    f"{DIST_INFO}/METADATA": (
        f"Metadata-Version: 2.1\nName: toetra\nVersion: {PROJECT_VERSION}\n\n".encode()
    ),
    f"{DIST_INFO}/WHEEL": b"Wheel-Version: 1.0\nTag: py3-none-any\n",
    f"{DIST_INFO}/RECORD": b"",
}


def _write_wheel(
    path: Path,
    *,
    leak_tests: bool = False,
    include_public_example: bool = True,
    forbidden_package: str | None = None,
) -> None:
    with zipfile.ZipFile(path, mode="w") as archive:
        for name, payload in WHEEL_MEMBERS.items():
            if (
                not include_public_example
                and name == "toetra/examples/credit_risk_policy.toetra"
            ):
                continue
            archive.writestr(name, payload)
        if leak_tests:
            archive.writestr("test/test_leak.py", b"")
        if forbidden_package is not None:
            archive.writestr(f"{forbidden_package}/__init__.py", b"")


def _write_sdist(path: Path, *, mtime: int) -> None:
    members = {
        f"{SDIST_ROOT}/LICENSE": b"license\n",
        f"{SDIST_ROOT}/README.md": b"readme\n",
        f"{SDIST_ROOT}/CHANGELOG.md": b"changelog\n",
        f"{SDIST_ROOT}/pyproject.toml": (
            f"[project]\nname='toetra'\nversion='{PROJECT_VERSION}'\n".encode()
        ),
        f"{SDIST_ROOT}/src/toetra/__init__.py": b"",
        f"{SDIST_ROOT}/src/toetra/_language/grammar/toetra_grammar.ebnf": (
            b"start=program\n"
        ),
        f"{SDIST_ROOT}/src/toetra/_language/grammar/toetra_grammar.lark": (
            b"start: program\n"
        ),
        f"{SDIST_ROOT}/src/toetra/examples/credit_risk_policy.toetra": (
            b"target := risk_score\n"
        ),
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
    _write_wheel(tmp_path / f"toetra-{PROJECT_VERSION}-py3-none-any.whl")
    _write_sdist(tmp_path / f"toetra-{PROJECT_VERSION}.tar.gz", mtime=100)

    artifacts = check_distribution_directory(tmp_path)

    assert artifacts.wheel.name.endswith(".whl")
    assert artifacts.sdist.name.endswith(".tar.gz")


@pytest.mark.parametrize("package", ["forml", "dsl", "model"])
def test_distribution_contract_rejects_forbidden_top_level_packages(
    tmp_path: Path,
    package: str,
) -> None:
    _write_wheel(
        tmp_path / f"toetra-{PROJECT_VERSION}-py3-none-any.whl",
        forbidden_package=package,
    )
    _write_sdist(tmp_path / f"toetra-{PROJECT_VERSION}.tar.gz", mtime=100)

    with pytest.raises(DistributionContractError, match="forbidden top-level package"):
        check_distribution_directory(tmp_path)


def test_distribution_contract_rejects_repository_paths_in_wheel(
    tmp_path: Path,
) -> None:
    _write_wheel(
        tmp_path / f"toetra-{PROJECT_VERSION}-py3-none-any.whl",
        leak_tests=True,
    )
    _write_sdist(tmp_path / f"toetra-{PROJECT_VERSION}.tar.gz", mtime=100)

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


def test_distribution_contract_rejects_missing_public_example(tmp_path: Path) -> None:
    _write_wheel(
        tmp_path / f"toetra-{PROJECT_VERSION}-py3-none-any.whl",
        include_public_example=False,
    )
    _write_sdist(tmp_path / f"toetra-{PROJECT_VERSION}.tar.gz", mtime=100)

    with pytest.raises(DistributionContractError, match="credit_risk_policy"):
        check_distribution_directory(tmp_path)


def test_release_source_accepts_a_clean_git_checkout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class Completed:
        stdout = ""

    monkeypatch.setattr(
        "scripts.release.distribution.subprocess.run",
        lambda *args, **kwargs: Completed(),
    )

    ensure_clean_repository(tmp_path)


def test_release_source_rejects_a_dirty_git_checkout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class Completed:
        stdout = " M src/toetra/_runtime/replay.py\n?? local.patch\n"

    monkeypatch.setattr(
        "scripts.release.distribution.subprocess.run",
        lambda *args, **kwargs: Completed(),
    )

    with pytest.raises(DistributionContractError, match="clean Git checkout"):
        ensure_clean_repository(tmp_path)
