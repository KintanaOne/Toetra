from __future__ import annotations

import tomllib
from pathlib import Path

from scripts.check_public_contract import (
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
    assert report_schema_version() == 5


def test_readme_points_to_the_authoritative_v1_profile() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "docs/public-v1-profile.md" in readme
    assert "forml.real_affine_extracted_model" in readme
    assert "Apache License 2.0" in readme
