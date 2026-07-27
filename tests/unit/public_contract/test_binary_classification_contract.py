from __future__ import annotations

from pathlib import Path

from scripts.ci.check_public_contract import (
    CLASSIFICATION_AMENDED_DOCUMENTS,
    CLASSIFICATION_TARGET_DOCUMENTS,
    EXPECTED_VERSION,
    _validate_classification_target_contract,
)

ROOT = Path(__file__).parents[3]


def test_patch_21_normative_documents_are_public_for_rc2() -> None:
    assert all(document.is_file() for document in CLASSIFICATION_TARGET_DOCUMENTS)
    assert all(document.is_file() for document in CLASSIFICATION_AMENDED_DOCUMENTS)
    for document in CLASSIFICATION_TARGET_DOCUMENTS[:6]:
        source = document.read_text(encoding="utf-8")
        assert "1.0.0rc2" in source
        assert "public adoption pending" not in source


def test_decision_and_property_thresholds_remain_distinct() -> None:
    profile = (
        ROOT / "docs" / "contracts" / "binary-classification-profile.md"
    ).read_text(encoding="utf-8")
    assert "strictly greater than `0.5`" in profile
    assert "Equality boundary" in profile
    assert "negative label" in profile
    assert "property threshold" in profile


def test_initial_route_and_rejections_are_explicit() -> None:
    profile = (
        ROOT / "docs" / "contracts" / "binary-classification-profile.md"
    ).read_text(encoding="utf-8")
    for marker in (
        "direct fitted `sklearn.linear_model.LogisticRegression`",
        "multiclass estimator",
        "`FixedThresholdClassifier`",
        "`TunedThresholdClassifierCV`",
        "`CalibratedClassifierCV`",
        "sklearn `Pipeline`",
    ):
        assert marker in profile


def test_rc3_public_profile_preserves_regression_and_binary_classification() -> None:
    public_profile = (ROOT / "docs" / "public-v1-profile.md").read_text(
        encoding="utf-8"
    )
    assert EXPECTED_VERSION == "1.0.0rc3"
    assert "Release candidate: `1.0.0rc3`" in public_profile
    assert "fitted single-output `LinearRegression`" in public_profile
    assert "direct fitted binary `LogisticRegression`" in public_profile
    assert "target[point].probability(label)" in public_profile


def test_patch_21_public_contract_validator_accepts_repository() -> None:
    _validate_classification_target_contract()
