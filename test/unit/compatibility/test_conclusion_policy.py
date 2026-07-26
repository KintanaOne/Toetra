from __future__ import annotations

from toetra._backends.results import VerificationResult, VerificationStatus
from toetra._compatibility.descriptors import PropertyNumericRequirements
from toetra._compatibility.enums import (
    CompatibilityClassification,
    ConclusionKind,
    ConclusionScope,
    SupportStatus,
)
from toetra._compatibility.model import (
    NumericCompatibilityAssessment,
    NumericCompatibilityQuery,
)
from toetra._compatibility.policy import (
    NUMERIC_CONCLUSION_NOT_PERMITTED,
    apply_numeric_compatibility_policy,
)
from toetra._language.vocabulary.backends import EnumBackend


def _assessment(
    permitted: frozenset[ConclusionKind],
) -> NumericCompatibilityAssessment:
    query = NumericCompatibilityQuery(
        framework_adapter_id="framework",
        framework_version=None,
        model_family="model",
        source_execution_profile_id="source",
        model_encoder_id="encoder",
        model_encoder_version="1",
        backend_kind="smt",
        backend_adapter_id="solver",
        backend_profile_id="profile",
        backend_version=None,
        property_numeric_requirements=PropertyNumericRequirements(),
    )
    return NumericCompatibilityAssessment(
        query=query,
        support_status=SupportStatus.SUPPORTED,
        classification=CompatibilityClassification.SOUND_UNDER_APPROXIMATION,
        semantic_target="source-model",
        permitted_conclusions=permitted,
        conclusion_scope=ConclusionScope.SOURCE_ARTIFACT,
        matched_rule_id="rule",
    )


def test_policy_downgrades_a_non_permitted_proof_to_unknown() -> None:
    result = VerificationResult(
        status=VerificationStatus.PROVED,
        backend=EnumBackend.Z3,
        backend_status="unsat",
        message="proved",
    )

    interpreted = apply_numeric_compatibility_policy(
        result,
        _assessment(frozenset({ConclusionKind.UNIVERSAL_COUNTEREXAMPLE})),
    )

    assert interpreted.status is VerificationStatus.UNKNOWN
    assert interpreted.metadata["backend_interpreted_status"] == "proved"
    assert interpreted.diagnostics[0].code == NUMERIC_CONCLUSION_NOT_PERMITTED


def test_policy_keeps_a_permitted_conclusion_and_attaches_provenance() -> None:
    result = VerificationResult(
        status=VerificationStatus.COUNTEREXAMPLE,
        backend=EnumBackend.Z3,
        backend_status="sat",
        message="counterexample",
    )

    interpreted = apply_numeric_compatibility_policy(
        result,
        _assessment(frozenset({ConclusionKind.UNIVERSAL_COUNTEREXAMPLE})),
    )

    assert interpreted.status is VerificationStatus.COUNTEREXAMPLE
    assert interpreted.metadata["numeric_compatibility"]["matched_rule_id"] == "rule"
