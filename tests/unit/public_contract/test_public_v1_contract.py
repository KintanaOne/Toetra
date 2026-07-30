from __future__ import annotations

import tomllib
from pathlib import Path

from scripts.ci.check_public_contract import (
    EXPECTED_LICENSE,
    EXPECTED_VERSION,
    check_public_contract,
    report_schema_version,
)

ROOT = Path(__file__).parents[3]


def test_public_contract_checker_accepts_repository() -> None:
    check_public_contract()


def test_public_version_license_and_json_contract_are_frozen() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]

    assert project["version"] == EXPECTED_VERSION
    assert project["license"] == EXPECTED_LICENSE
    assert "scripts" not in project
    assert report_schema_version() == 6


def test_readme_points_to_the_authoritative_v1_profile() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "docs/public-v1-profile.md" in readme
    assert "LinearRegression" in readme
    assert "LogisticRegression" in readme
    assert "Apache License 2.0" in readme


def test_sdist_manifest_includes_public_release_files() -> None:
    manifest = (ROOT / "MANIFEST.in").read_text(encoding="utf-8")

    assert "include CHANGELOG.md" in manifest
    assert "include LICENSE" in manifest
    assert "include README.md" in manifest
    assert "include pyproject.toml" in manifest
