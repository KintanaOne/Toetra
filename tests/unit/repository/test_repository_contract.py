from __future__ import annotations

from pathlib import Path

import pytest

from scripts.repository import check_repository_contract as repository_contract

ROOT = Path(__file__).parents[3]


def test_current_repository_satisfies_the_frozen_p24_contract() -> None:
    assert repository_contract.repository_contract_errors(ROOT) == ()


def test_repository_contract_reports_public_api_drift(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        repository_contract,
        "EXPECTED_PUBLIC_API",
        (*repository_contract.EXPECTED_PUBLIC_API, "accidental_export"),
    )

    with pytest.raises(
        repository_contract.RepositoryContractError,
        match="Public facade differs",
    ):
        repository_contract.validate_repository_contract(ROOT)
