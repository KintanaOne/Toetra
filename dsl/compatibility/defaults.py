from __future__ import annotations

from dsl.compatibility.enums import (
    BackendKind,
    CompatibilityClassification,
    ConclusionKind,
    ConclusionScope,
    SupportStatus,
)
from dsl.compatibility.model import CompatibilityRule, CompatibilityRulePattern
from dsl.compatibility.registry import NumericCompatibilityRegistry

SKLEARN_AFFINE_TO_EXACT_REAL_RULE_ID = (
    "forml.v1.sklearn-affine-to-smt-exact-real-abstraction"
)


def create_default_numeric_compatibility_registry() -> NumericCompatibilityRegistry:
    """Create the built-in compatibility rules used by the V1 runtime."""

    registry = NumericCompatibilityRegistry()
    registry.register(
        CompatibilityRule(
            rule_id=SKLEARN_AFFINE_TO_EXACT_REAL_RULE_ID,
            pattern=CompatibilityRulePattern(
                framework_adapter_id="sklearn",
                model_family="affine_regression",
                model_encoder_id="forml.affine-equation",
                model_encoder_version="1",
                backend_kind=BackendKind.SMT.value,
                backend_adapter_id="z3",
                backend_profile_id="smt_real_affine_exact",
            ),
            support_status=SupportStatus.SUPPORTED,
            classification=CompatibilityClassification.LOSSY,
            semantic_target="forml.real_affine_extracted_model",
            evidence_id="ADR-0018#initial-v1-instantiation",
            permitted_conclusions=frozenset(ConclusionKind),
            conclusion_scope=ConclusionScope.SEMANTIC_TARGET_ONLY,
            assumptions_and_preconditions=(
                "The model family is affine regression.",
                "All encoded numeric contributors are finite.",
                "Conclusions apply to the extracted real-affine abstraction, "
                "not bit-exact framework execution.",
            ),
            replay_required_for=frozenset(
                {
                    ConclusionKind.UNIVERSAL_COUNTEREXAMPLE,
                    ConclusionKind.EXISTENTIAL_WITNESS,
                }
            ),
            diagnostics=(
                "Concrete floating-point execution is not proven equivalent to "
                "the exact-real affine encoding.",
            ),
            documentation_reference=(
                "docs/adr/ADR-0018-numeric-semantics-and-backend-compatibility.md"
            ),
        )
    )
    return registry
