from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_identity_contract import (
    IdentityContractError,
    check_identity_contract,
    collect_identity_violations,
)


def test_repository_satisfies_toetra_identity_contract() -> None:
    check_identity_contract()


def test_identity_contract_rejects_unapproved_legacy_branding(
    tmp_path: Path,
) -> None:
    (tmp_path / "README.md").write_text(
        "The FORML package accepts policy.forml.\n",
        encoding="utf-8",
    )

    violations = collect_identity_violations(tmp_path)

    assert [(item.path, item.line_number) for item in violations] == [("README.md", 1)]
    with pytest.raises(IdentityContractError, match="README.md:1"):
        check_identity_contract(tmp_path)


def test_identity_contract_allows_documented_historical_record(
    tmp_path: Path,
) -> None:
    path = tmp_path / "docs" / "adr" / "ADR-0027-adopt-toetra-as-canonical-identity.md"
    path.parent.mkdir(parents=True)
    path.write_text("FORML and .forml are historical names.\n", encoding="utf-8")

    assert collect_identity_violations(tmp_path) == ()
