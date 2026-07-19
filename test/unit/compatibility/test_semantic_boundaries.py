from __future__ import annotations

import pytest

from dsl.backends.results import VerificationResult, VerificationStatus
from dsl.compatibility.descriptors import PropertyNumericRequirements
from dsl.compatibility.enums import (
    CompatibilityClassification,
    ConclusionKind,
    ConclusionScope,
    SupportStatus,
)
from dsl.compatibility.model import (
    NumericCompatibilityAssessment,
    NumericCompatibilityQuery,
)
from dsl.compatibility.policy import apply_numeric_compatibility_policy
from dsl.language.vocabulary.backends import EnumBackend

_STATUS_TO_CONCLUSION = {
    VerificationStatus.PROVED: ConclusionKind.UNIVERSAL_PROOF,
    VerificationStatus.COUNTEREXAMPLE: ConclusionKind.UNIVERSAL_COUNTEREXAMPLE,
    VerificationStatus.WITNESS: ConclusionKind.EXISTENTIAL_WITNESS,
    VerificationStatus.NO_WITNESS: ConclusionKind.EXISTENTIAL_NO_WITNESS,
}


def _assessment(
    classification: CompatibilityClassification,
    permitted: frozenset[ConclusionKind],
    *,
    scope: ConclusionScope = ConclusionScope.SOURCE_ARTIFACT,
) -> NumericCompatibilityAssessment:
    return NumericCompatibilityAssessment(
        query=NumericCompatibilityQuery(
            framework_adapter_id="framework",
            framework_version=None,
            model_family="model",
            source_execution_profile_id="source",
            model_encoder_id="encoder",
            model_encoder_version="1",
            backend_kind="backend-kind",
            backend_adapter_id="backend",
            backend_profile_id="profile",
            backend_version=None,
            property_numeric_requirements=PropertyNumericRequirements(),
        ),
        support_status=SupportStatus.SUPPORTED,
        classification=classification,
        semantic_target="semantic-target",
        permitted_conclusions=permitted,
        conclusion_scope=scope,
        matched_rule_id=f"rule-{classification.value}",
    )


def _result(status: VerificationStatus) -> VerificationResult:
    return VerificationResult(
        status=status,
        backend=EnumBackend.Z3,
        backend_status="backend-status",
        message=status.value,
    )


@pytest.mark.parametrize(
    ("classification", "permitted"),
    (
        (
            CompatibilityClassification.EXACT,
            frozenset(ConclusionKind),
        ),
        (
            CompatibilityClassification.SOUND_OVER_APPROXIMATION,
            frozenset(
                {
                    ConclusionKind.UNIVERSAL_PROOF,
                    ConclusionKind.EXISTENTIAL_NO_WITNESS,
                }
            ),
        ),
        (
            CompatibilityClassification.SOUND_UNDER_APPROXIMATION,
            frozenset(
                {
                    ConclusionKind.UNIVERSAL_COUNTEREXAMPLE,
                    ConclusionKind.EXISTENTIAL_WITNESS,
                }
            ),
        ),
    ),
)
@pytest.mark.parametrize("status", tuple(_STATUS_TO_CONCLUSION))
def test_source_artifact_conclusions_fail_closed_at_semantic_boundaries(
    classification: CompatibilityClassification,
    permitted: frozenset[ConclusionKind],
    status: VerificationStatus,
) -> None:
    interpreted = apply_numeric_compatibility_policy(
        _result(status),
        _assessment(classification, permitted),
    )

    conclusion = _STATUS_TO_CONCLUSION[status]
    expected = status if conclusion in permitted else VerificationStatus.UNKNOWN
    assert interpreted.status is expected


def test_lossy_route_can_report_results_only_for_its_named_semantic_target() -> None:
    assessment = _assessment(
        CompatibilityClassification.LOSSY,
        frozenset(ConclusionKind),
        scope=ConclusionScope.SEMANTIC_TARGET_ONLY,
    )

    interpreted = apply_numeric_compatibility_policy(
        _result(VerificationStatus.PROVED),
        assessment,
    )

    assert interpreted.status is VerificationStatus.PROVED
    provenance = interpreted.metadata["numeric_compatibility"]
    assert provenance["classification"] == "lossy"
    assert provenance["semantic_target"] == "semantic-target"
    assert provenance["conclusion_scope"] == "semantic_target_only"


def test_unknown_backend_result_is_never_promoted_by_numeric_policy() -> None:
    interpreted = apply_numeric_compatibility_policy(
        _result(VerificationStatus.UNKNOWN),
        _assessment(
            CompatibilityClassification.EXACT,
            frozenset(ConclusionKind),
        ),
    )

    assert interpreted.status is VerificationStatus.UNKNOWN
    assert "backend_interpreted_status" not in interpreted.metadata
