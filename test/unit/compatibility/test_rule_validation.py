from __future__ import annotations

import pytest

from dsl.compatibility.enums import (
    CompatibilityClassification,
    ConclusionKind,
    ConclusionScope,
    SupportStatus,
)
from dsl.compatibility.errors import InvalidCompatibilityRuleError
from dsl.compatibility.model import CompatibilityRule, CompatibilityRulePattern


def test_lossy_source_artifact_rule_cannot_claim_a_universal_proof() -> None:
    with pytest.raises(InvalidCompatibilityRuleError):
        CompatibilityRule(
            rule_id="invalid-lossy-proof",
            pattern=CompatibilityRulePattern(),
            support_status=SupportStatus.SUPPORTED,
            classification=CompatibilityClassification.LOSSY,
            semantic_target="source-model",
            evidence_id="none",
            permitted_conclusions=frozenset({ConclusionKind.UNIVERSAL_PROOF}),
            conclusion_scope=ConclusionScope.SOURCE_ARTIFACT,
        )


def test_lossy_rule_may_prove_an_explicitly_named_abstraction() -> None:
    rule = CompatibilityRule(
        rule_id="abstraction-proof",
        pattern=CompatibilityRulePattern(),
        support_status=SupportStatus.SUPPORTED,
        classification=CompatibilityClassification.LOSSY,
        semantic_target="real-affine-abstraction",
        evidence_id="adr",
        permitted_conclusions=frozenset({ConclusionKind.UNIVERSAL_PROOF}),
        conclusion_scope=ConclusionScope.SEMANTIC_TARGET_ONLY,
    )

    assert rule.semantic_target == "real-affine-abstraction"


def test_over_approximation_source_rule_cannot_claim_a_counterexample() -> None:
    with pytest.raises(InvalidCompatibilityRuleError):
        CompatibilityRule(
            rule_id="invalid-over-counterexample",
            pattern=CompatibilityRulePattern(),
            support_status=SupportStatus.SUPPORTED,
            classification=CompatibilityClassification.SOUND_OVER_APPROXIMATION,
            semantic_target="source-model",
            evidence_id="none",
            permitted_conclusions=frozenset({ConclusionKind.UNIVERSAL_COUNTEREXAMPLE}),
            conclusion_scope=ConclusionScope.SOURCE_ARTIFACT,
        )


def test_under_approximation_source_rule_may_claim_concrete_candidates() -> None:
    rule = CompatibilityRule(
        rule_id="under-candidates",
        pattern=CompatibilityRulePattern(),
        support_status=SupportStatus.SUPPORTED,
        classification=CompatibilityClassification.SOUND_UNDER_APPROXIMATION,
        semantic_target="source-model",
        evidence_id="evidence",
        permitted_conclusions=frozenset(
            {
                ConclusionKind.UNIVERSAL_COUNTEREXAMPLE,
                ConclusionKind.EXISTENTIAL_WITNESS,
            }
        ),
        conclusion_scope=ConclusionScope.SOURCE_ARTIFACT,
    )

    assert rule.permitted_conclusions == frozenset(
        {
            ConclusionKind.UNIVERSAL_COUNTEREXAMPLE,
            ConclusionKind.EXISTENTIAL_WITNESS,
        }
    )


def test_replay_requirements_must_be_candidate_conclusions_and_permitted() -> None:
    with pytest.raises(InvalidCompatibilityRuleError):
        CompatibilityRule(
            rule_id="invalid-replay",
            pattern=CompatibilityRulePattern(),
            support_status=SupportStatus.SUPPORTED,
            classification=CompatibilityClassification.EXACT,
            semantic_target="source-model",
            evidence_id="evidence",
            permitted_conclusions=frozenset({ConclusionKind.UNIVERSAL_PROOF}),
            replay_required_for=frozenset({ConclusionKind.UNIVERSAL_PROOF}),
            conclusion_scope=ConclusionScope.SOURCE_ARTIFACT,
        )
