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
    repository = root / "Toetra"
    repository.mkdir()
    for raw_path in CRITICAL_PATHS:
        path = repository / raw_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"fixture for {raw_path}\n", encoding="utf-8")
    module_path = repository / "src" / "toetra" / "_runtime" / "module.py"
    module_path.parent.mkdir(parents=True, exist_ok=True)
    module_path.write_text("VALUE = 1\n", encoding="utf-8")
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
        assert manifest["bundle_kind"] == "toetra_review_source_snapshot"
        assert manifest["repository_root_name"] == "Toetra"
        assert manifest["missing_critical_paths"] == []
        assert "src/toetra/__init__.py" in archive.namelist()
        assert not any("__pycache__" in name for name in archive.namelist())


def test_review_bundle_excludes_sensitive_files_without_dropping_review_assets(
    tmp_path: Path,
) -> None:
    repository = _complete_repository(tmp_path)
    sensitive_paths = (
        ".env",
        ".env.local",
        "config/credentials.json",
        "config/private.pem",
        "keys/id_ed25519",
    )
    for raw_path in sensitive_paths:
        path = repository / raw_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("secret\n", encoding="utf-8")

    csv_path = (
        repository / "demo" / "classification" / "cleveland" / "data" / "review.csv"
    )
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.write_text("feature,target\n1,0\n", encoding="utf-8")
    notebook_path = repository / "demo" / "regression" / "review.ipynb"
    notebook_path.parent.mkdir(parents=True, exist_ok=True)
    notebook_path.write_text("{}\n", encoding="utf-8")

    bundle = build_review_bundle(repository, tmp_path / "bundle.zip")

    with zipfile.ZipFile(bundle.path) as archive:
        names = set(archive.namelist())
        assert not names.intersection(sensitive_paths)
        assert "demo/classification/cleveland/data/review.csv" in names
        assert "demo/regression/review.ipynb" in names


def test_review_bundle_refuses_missing_critical_paths(tmp_path: Path) -> None:
    repository = tmp_path / "Toetra"
    repository.mkdir()
    (repository / "README.md").write_text("Toetra\n", encoding="utf-8")

    with pytest.raises(ReviewBundleError, match="missing critical paths"):
        build_review_bundle(repository, tmp_path / "bundle.zip")
