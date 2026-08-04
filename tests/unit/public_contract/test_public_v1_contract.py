from __future__ import annotations

import tomllib
from pathlib import Path

from scripts.ci.check_public_contract import (
    EXPECTED_INSPECTION_SCHEMA,
    EXPECTED_LICENSE,
    EXPECTED_PROJECT_SCRIPTS,
    EXPECTED_RUN_MANIFEST_SCHEMA,
    EXPECTED_VALIDATION_SCHEMA,
    EXPECTED_VERSION,
    check_public_contract,
    cli_run_manifest_contract,
    cli_schema_contracts,
    report_schema_version,
)

ROOT = Path(__file__).parents[3]


def test_public_contract_checker_accepts_repository() -> None:
    check_public_contract()


def test_public_version_license_cli_and_json_contract_are_frozen() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]

    assert project["version"] == EXPECTED_VERSION
    assert project["license"] == EXPECTED_LICENSE
    assert project["license-files"] == ["LICENSE", "COPYRIGHT.md"]
    assert project["scripts"] == EXPECTED_PROJECT_SCRIPTS
    assert report_schema_version() == 6
    assert cli_schema_contracts() == (
        EXPECTED_VALIDATION_SCHEMA,
        EXPECTED_INSPECTION_SCHEMA,
    )
    assert cli_run_manifest_contract() == EXPECTED_RUN_MANIFEST_SCHEMA


def test_readme_points_to_the_authoritative_v1_profile() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "docs/public-v1-profile.md" in readme
    assert "not currently published on PyPI" in readme
    assert "source checkout or source archive" in readme
    assert "python -m demo.quickstart.verify_model --demo" in readme
    assert "toetra verify" in readme
    assert "LinearRegression" in readme
    assert "LogisticRegression" in readme
    assert "PolyForm Noncommercial License 1.0.0" in readme
    assert "COMMERCIAL_LICENSE.md" in readme
    assert "COPYRIGHT.md" in readme
    assert "Tina RANDRIANARIJAONA-DUBIN" in readme
    assert "not an open-source license" in readme
    assert "CONTRIBUTING.md" in readme
    assert "SECURITY.md" in readme


def test_installation_does_not_claim_unavailable_distribution_surfaces() -> None:
    installation = (ROOT / "docs" / "getting-started" / "installation.md").read_text(
        encoding="utf-8"
    )

    assert "not the stable `1.0.0` release" in installation
    assert "not currently published on PyPI" in installation
    assert "pip install toetra" in installation
    assert "is not a documented installation path" in installation
    assert "python -m pip install ." in installation


def test_sdist_manifest_includes_public_release_files() -> None:
    manifest = (ROOT / "MANIFEST.in").read_text(encoding="utf-8")

    assert "include CHANGELOG.md" in manifest
    assert "include COMMERCIAL_LICENSE.md" in manifest
    assert "include COPYRIGHT.md" in manifest
    assert "include LICENSE" in manifest
    assert "include README.md" in manifest
    assert "include pyproject.toml" in manifest
