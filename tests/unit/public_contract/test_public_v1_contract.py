from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from scripts.ci import check_public_contract as contract
from scripts.ci.check_public_contract import (
    EXPECTED_INSPECTION_SCHEMA,
    EXPECTED_LICENSE,
    EXPECTED_MATURITY,
    EXPECTED_PROJECT_SCRIPTS,
    EXPECTED_REPLAY_SCHEMA,
    EXPECTED_RUN_MANIFEST_SCHEMA,
    EXPECTED_VALIDATION_SCHEMA,
    EXPECTED_VERSION,
    check_public_contract,
    cli_replay_contract,
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
    assert EXPECTED_MATURITY in project["classifiers"]
    assert project["license"] == EXPECTED_LICENSE
    assert project["license-files"] == ["LICENSE", "COPYRIGHT.md"]
    assert project["scripts"] == EXPECTED_PROJECT_SCRIPTS
    assert report_schema_version() == 6
    assert cli_schema_contracts() == (
        EXPECTED_VALIDATION_SCHEMA,
        EXPECTED_INSPECTION_SCHEMA,
    )
    assert cli_run_manifest_contract() == EXPECTED_RUN_MANIFEST_SCHEMA
    assert cli_replay_contract() == EXPECTED_REPLAY_SCHEMA


def test_readme_points_to_the_authoritative_v1_profile() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "docs/public-v1-profile.md" in readme
    assert "not currently published on PyPI" in readme
    assert "source checkout or source archive" in readme
    assert "python -m demo.quickstart.verify_model --demo" in readme
    assert "toetra verify" in readme
    assert "toetra replay" in readme
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

    assert "stable `1.0.0` sources are prepared for publication" in installation
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


@pytest.mark.parametrize(
    ("name", "before", "after", "message"),
    (
        (
            "README.md",
            "Project status — `1.0.0`",
            "Project status — `1.0.0rc4`",
            "prepared stable source status",
        ),
        (
            "website/index.html",
            "prepared for publication",
            "evaluation release",
            "prepared stable source status",
        ),
        (
            "docs/releases/1.0.0.md",
            "Publication remains pending",
            "Publication completed",
            "prepared stable source status",
        ),
        (
            "docs/releases/1.0.0rc4.md",
            "evaluation release candidate",
            "stable release",
            "Historical RC4 release status",
        ),
        (
            "docs/cli/overview.md",
            "`1.0.0` implements",
            "`1.0.0rc4` implements",
            "current stable version",
        ),
        (
            "mkdocs.yml",
            "releases/1.0.0.md",
            "releases/1.0.0rc4.md",
            "MkDocs must link",
        ),
    ),
)
def test_narrative_rejects_version_status_and_history_regressions(
    monkeypatch: pytest.MonkeyPatch,
    name: str,
    before: str,
    after: str,
    message: str,
) -> None:
    original_read = Path.read_text
    target = ROOT / name
    assert before in target.read_text(encoding="utf-8")

    def read_text(
        path: Path, encoding: str | None = None, errors: str | None = None
    ) -> str:
        source = original_read(path, encoding=encoding, errors=errors)
        return source.replace(before, after) if path == target else source

    monkeypatch.setattr(Path, "read_text", read_text)
    with pytest.raises(contract.PublicContractError, match=message):
        contract._validate_public_narrative()


@pytest.mark.parametrize(
    "claim",
    (
        "pip install toetra",
        "python -m pip install --upgrade toetra==1.0.0",
        'python3 -m pip install "toetra[dev]"',
        "pip3 install --pre toetra",
        "Toetra is now published on PyPI.",
        "Version 1.0.0 is available on GitHub.",
    ),
)
def test_narrative_rejects_premature_distribution_claims(
    monkeypatch: pytest.MonkeyPatch, claim: str
) -> None:
    original_read = Path.read_text

    def read_text(
        path: Path, encoding: str | None = None, errors: str | None = None
    ) -> str:
        source = original_read(path, encoding=encoding, errors=errors)
        return source + "\n" + claim + "\n" if path == ROOT / "README.md" else source

    monkeypatch.setattr(Path, "read_text", read_text)
    with pytest.raises(contract.PublicContractError, match="unavailable|premature"):
        contract._validate_public_narrative()


@pytest.mark.parametrize(
    "classifiers",
    (
        [],
        ["Development Status :: 4 - Beta"],
        [contract.EXPECTED_MATURITY, "Development Status :: 4 - Beta"],
    ),
)
def test_contract_rejects_missing_or_conflicting_stable_maturity(
    monkeypatch: pytest.MonkeyPatch, classifiers: list[str]
) -> None:
    project = dict(contract._project(), classifiers=classifiers)
    monkeypatch.setattr(contract, "_project", lambda: project)
    with pytest.raises(contract.PublicContractError, match="maturity classifier"):
        check_public_contract()
