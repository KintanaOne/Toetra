from __future__ import annotations

import hashlib
import io
import tarfile
import zipfile
from pathlib import Path

import pytest

from scripts.release.check_pypi_artifacts import validate_pypi_artifacts


def _archives(tmp_path: Path, *, metadata_version: str = "1.0.0") -> tuple[Path, Path]:
    project = tmp_path / "pyproject.toml"
    project.write_text('[project]\nname="toetra"\nversion="1.0.0"\n')
    dist = tmp_path / "dist"
    dist.mkdir()
    metadata = f"Name: toetra\nVersion: {metadata_version}\n".encode()
    with zipfile.ZipFile(dist / "toetra-1.0.0-py3-none-any.whl", "w") as wheel:
        wheel.writestr("toetra-1.0.0.dist-info/METADATA", metadata)
    with tarfile.open(dist / "toetra-1.0.0.tar.gz", "w:gz") as sdist:
        info = tarfile.TarInfo("toetra-1.0.0/PKG-INFO")
        info.size = len(metadata)
        sdist.addfile(info, io.BytesIO(metadata))
    (dist / "SHA256SUMS").write_text(
        "".join(
            f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n"
            for path in sorted(dist.iterdir())
        )
    )
    return dist, project


def test_pypi_accepts_verified_stable_archives(tmp_path: Path) -> None:
    dist, project = _archives(tmp_path)
    validate_pypi_artifacts(dist, version="1.0.0", project_file=project)


@pytest.mark.parametrize("version", ["", "1.0.0rc4", "1.0.1", "01.0.0", "../1.0.0"])
def test_pypi_rejects_wrong_or_nonstable_version(tmp_path: Path, version: str) -> None:
    dist, project = _archives(tmp_path)
    with pytest.raises(ValueError):
        validate_pypi_artifacts(dist, version=version, project_file=project)


def test_pypi_rejects_modified_archive(tmp_path: Path) -> None:
    dist, project = _archives(tmp_path)
    (dist / "toetra-1.0.0-py3-none-any.whl").write_bytes(b"modified")
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        validate_pypi_artifacts(dist, version="1.0.0", project_file=project)


def test_pypi_rejects_metadata_from_another_version(tmp_path: Path) -> None:
    dist, project = _archives(tmp_path, metadata_version="1.0.0rc4")
    with pytest.raises(ValueError, match="Unexpected project or version"):
        validate_pypi_artifacts(dist, version="1.0.0", project_file=project)


@pytest.mark.parametrize("mutation", ["duplicate", "missing", "path", "extra"])
def test_pypi_rejects_ambiguous_inventory(tmp_path: Path, mutation: str) -> None:
    dist, project = _archives(tmp_path)
    manifest = dist / "SHA256SUMS"
    lines = manifest.read_text().splitlines(keepends=True)
    if mutation == "duplicate":
        manifest.write_text("".join(lines + lines[:1]))
    elif mutation == "missing":
        manifest.write_text(lines[0])
    elif mutation == "path":
        manifest.write_text("".join(lines).replace("  toetra-", "  ../toetra-"))
    else:
        (dist / "unexpected.whl").write_bytes(b"extra")
    with pytest.raises(ValueError):
        validate_pypi_artifacts(dist, version="1.0.0", project_file=project)
