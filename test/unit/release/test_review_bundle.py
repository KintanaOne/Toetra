from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from scripts.release.review_bundle import (
    CRITICAL_PATHS,
    ReviewBundleError,
    build_review_bundle,
    check_review_bundle_reproducibility,
)


def _complete_repository(root: Path) -> Path:
    repository = root / "FORML"
    repository.mkdir()
    for raw_path in CRITICAL_PATHS:
        path = repository / raw_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"fixture for {raw_path}\n", encoding="utf-8")
    (repository / "dsl" / "module.py").write_text("VALUE = 1\n", encoding="utf-8")
    return repository


def test_review_bundle_is_byte_reproducible_and_manifested(tmp_path: Path) -> None:
    repository = _complete_repository(tmp_path)
    first = build_review_bundle(repository, tmp_path / "first.zip")
    second = build_review_bundle(repository, tmp_path / "second.zip")

    assert first.sha256 == second.sha256
    assert check_review_bundle_reproducibility(repository) == first.sha256

    with zipfile.ZipFile(first.path) as archive:
        manifest = json.loads(archive.read("_meta/manifest.json"))
        assert manifest["schema_version"] == 2
        assert manifest["missing_critical_paths"] == []
        assert "forml/__init__.py" in archive.namelist()
        assert not any("__pycache__" in name for name in archive.namelist())


def test_review_bundle_refuses_missing_critical_paths(tmp_path: Path) -> None:
    repository = tmp_path / "FORML"
    repository.mkdir()
    (repository / "README.md").write_text("FORML\n", encoding="utf-8")

    with pytest.raises(ReviewBundleError, match="missing critical paths"):
        build_review_bundle(repository, tmp_path / "bundle.zip")
