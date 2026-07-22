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
SKLEARN_BINARY_LOGISTIC_TO_EXACT_REAL_RULE_ID = (
    "forml.p21.sklearn-binary-logistic-to-smt-exact-real-abstraction"
)
SKLEARN_BINARY_LOGISTIC_PROBABILITY_RULE_ID = (
    "forml.p21.sklearn-binary-logistic-probability-to-smt-directed-bound"
)
SKLEARN_BINARY_LOGISTIC_EXACT_PROBABILITY_RULE_ID = (
    "forml.p21.sklearn-binary-logistic-probability-to-smt-exact-boundary"
)


def create_default_numeric_compatibility_registry() -> NumericCompatibilityRegistry:
    """Create the built-in compatibility rules used by the V1 runtime."""

    registry = NumericCompatibilityRegistry()
    registry.register(
        CompatibilityRule(
            rule_id=SKLEARN_BINARY_LOGISTIC_EXACT_PROBABILITY_RULE_ID,
            pattern=CompatibilityRulePattern(
                framework_adapter_id="sklearn",
                model_family="binary_logistic_affine_classifier",
                model_encoder_id="forml.binary-logistic-affine-equation",
                model_encoder_version="1",
                backend_kind=BackendKind.SMT.value,
                backend_adapter_id="z3",
                backend_profile_id="smt_real_affine_exact",
                required_property_tags=frozenset(
                    {
                        "model_semantic_quantities",
                        "affine_arithmetic",
                        "logistic_probability_threshold",
                    }
                ),
            ),
            support_status=SupportStatus.SUPPORTED,
            classification=CompatibilityClassification.LOSSY,
            semantic_target="forml.oriented-decision-value",
            evidence_id="ADR-0025#native-binary-decision-profile",
            permitted_conclusions=frozenset(ConclusionKind),
            conclusion_scope=ConclusionScope.SEMANTIC_TARGET_ONLY,
            assumptions_and_preconditions=(
                "The probability threshold is exactly 0.5 and lowers to the "
                "exact oriented decision boundary 0.",
                "The estimator is a direct fitted binary LogisticRegression.",
                "All encoded numeric contributors are finite.",
            ),
            replay_required_for=frozenset(
                {
                    ConclusionKind.UNIVERSAL_COUNTEREXAMPLE,
                    ConclusionKind.EXISTENTIAL_WITNESS,
                }
            ),
            diagnostics=(
                "The probability-to-decision lowering is exact at p = 0.5; "
                "framework floating-point extraction remains a lossy route.",
            ),
            documentation_reference=(
                "docs/adr/ADR-0025-binary-classification-profile.md"
            ),
        )
    )
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
    registry.register(
        CompatibilityRule(
            rule_id=SKLEARN_BINARY_LOGISTIC_TO_EXACT_REAL_RULE_ID,
            pattern=CompatibilityRulePattern(
                framework_adapter_id="sklearn",
                model_family="binary_logistic_affine_classifier",
                model_encoder_id="forml.binary-logistic-affine-equation",
                model_encoder_version="1",
                backend_kind=BackendKind.SMT.value,
                backend_adapter_id="z3",
                backend_profile_id="smt_real_affine_exact",
                required_property_tags=frozenset(
                    {"model_semantic_quantities", "affine_arithmetic"}
                ),
            ),
            support_status=SupportStatus.SUPPORTED,
            classification=CompatibilityClassification.LOSSY,
            semantic_target="forml.oriented-decision-value",
            evidence_id="ADR-0025#native-binary-decision-profile",
            permitted_conclusions=frozenset(ConclusionKind),
            conclusion_scope=ConclusionScope.SEMANTIC_TARGET_ONLY,
            assumptions_and_preconditions=(
                "The estimator is a direct fitted binary LogisticRegression.",
                "The native decision policy is probability > 0.5, equivalent "
                "to oriented decision value > 0.",
                "All encoded numeric contributors are finite.",
                "Conclusions apply to the extracted exact-real affine decision "
                "abstraction, not bit-exact sklearn execution.",
            ),
            replay_required_for=frozenset(
                {
                    ConclusionKind.UNIVERSAL_COUNTEREXAMPLE,
                    ConclusionKind.EXISTENTIAL_WITNESS,
                }
            ),
            diagnostics=(
                "Concrete floating-point decision execution is not proven "
                "bit-equivalent to the exact-real affine encoding.",
            ),
            documentation_reference=(
                "docs/adr/ADR-0025-binary-classification-profile.md"
            ),
        )
    )
    registry.register(
        CompatibilityRule(
            rule_id=SKLEARN_BINARY_LOGISTIC_PROBABILITY_RULE_ID,
            pattern=CompatibilityRulePattern(
                framework_adapter_id="sklearn",
                model_family="binary_logistic_affine_classifier",
                model_encoder_id="forml.binary-logistic-affine-equation",
                model_encoder_version="1",
                backend_kind=BackendKind.SMT.value,
                backend_adapter_id="z3",
                backend_profile_id="smt_real_affine_exact",
                required_property_tags=frozenset(
                    {
                        "model_semantic_quantities",
                        "affine_arithmetic",
                        "logistic_probability_threshold",
                        "transcendental_threshold_lowering",
                    }
                ),
            ),
            support_status=SupportStatus.SUPPORTED,
            classification=CompatibilityClassification.LOSSY,
            semantic_target="forml.oriented-decision-value-directed-bound",
            evidence_id="ADR-0024#probability-threshold-lowering",
            permitted_conclusions=frozenset(ConclusionKind),
            conclusion_scope=ConclusionScope.SEMANTIC_TARGET_ONLY,
            assumptions_and_preconditions=(
                "The estimator is a direct fitted binary LogisticRegression.",
                "The user threshold is strictly between 0 and 1.",
                "The exact logit threshold is enclosed by an outward decimal "
                "interval and one directed bound is selected according to "
                "logical polarity.",
                "The semantic-lowering conclusion policy is applied in "
                "addition to this framework/backend compatibility rule.",
                "All encoded numeric contributors are finite.",
            ),
            replay_required_for=frozenset(
                {
                    ConclusionKind.UNIVERSAL_COUNTEREXAMPLE,
                    ConclusionKind.EXISTENTIAL_WITNESS,
                }
            ),
            diagnostics=(
                "Non-exact probability thresholds use a directed decimal "
                "bound around logit(p); conclusions outside the lowering "
                "policy are downgraded to UNKNOWN.",
                "Concrete sklearn floating-point execution is not proven "
                "bit-equivalent to the exact-real affine encoding.",
            ),
            documentation_reference=("docs/adr/ADR-0024-model-semantic-lowering.md"),
        )
    )
    return registry
