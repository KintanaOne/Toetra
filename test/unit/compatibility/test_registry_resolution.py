from __future__ import annotations

import pytest

from toetra._compatibility.descriptors import (
    BackendProfileDescriptor,
    NumericSemanticDescriptor,
    PropertyNumericRequirements,
)
from toetra._compatibility.enums import (
    BackendKind,
    CompatibilityClassification,
    ConclusionKind,
    ConclusionScope,
    SupportStatus,
)
from toetra._compatibility.errors import (
    AmbiguousCompatibilityRuleError,
    DuplicateCompatibilityRuleError,
)
from toetra._compatibility.model import (
    CompatibilityRule,
    CompatibilityRulePattern,
    NumericCompatibilityQuery,
)
from toetra._compatibility.registry import NumericCompatibilityRegistry


def _backend_profile() -> BackendProfileDescriptor:
    return BackendProfileDescriptor(
        backend_kind=BackendKind.SMT,
        adapter_id="solver",
        profile_id="exact-real",
        numeric_semantics=NumericSemanticDescriptor.exact_real(),
    )


def _query(*, non_finite: bool = False) -> NumericCompatibilityQuery:
    return NumericCompatibilityQuery(
        framework_adapter_id="framework",
        framework_version="1.0",
        model_family="affine_regression",
        source_execution_profile_id="binary64",
        model_encoder_id="affine-encoder",
        model_encoder_version="1",
        backend_kind=BackendKind.SMT.value,
        backend_adapter_id="solver",
        backend_profile_id="exact-real",
        backend_version="2.0",
        property_numeric_requirements=PropertyNumericRequirements(
            frozenset({"numeric_comparisons", "affine_arithmetic"})
        ),
        contains_non_finite_values=non_finite,
    )


def _rule(
    rule_id: str,
    pattern: CompatibilityRulePattern,
    *,
    classification: CompatibilityClassification = CompatibilityClassification.EXACT,
) -> CompatibilityRule:
    return CompatibilityRule(
        rule_id=rule_id,
        pattern=pattern,
        support_status=SupportStatus.SUPPORTED,
        classification=classification,
        semantic_target="test-target",
        evidence_id=f"evidence:{rule_id}",
        permitted_conclusions=frozenset(ConclusionKind),
        conclusion_scope=ConclusionScope.SEMANTIC_TARGET_ONLY,
    )


def test_registry_prefers_the_most_specific_matching_rule() -> None:
    registry = NumericCompatibilityRegistry()
    registry.register(
        _rule(
            "generic",
            CompatibilityRulePattern(backend_kind=BackendKind.SMT.value),
        )
    )
    registry.register(
        _rule(
            "specific",
            CompatibilityRulePattern(
                framework_adapter_id="framework",
                model_family="affine_regression",
                backend_kind=BackendKind.SMT.value,
                backend_profile_id="exact-real",
                required_property_tags=frozenset({"affine_arithmetic"}),
            ),
        )
    )

    assessment = registry.assess(_query(), backend_profile=_backend_profile())

    assert assessment.matched_rule_id == "specific"
    assert assessment.classification is CompatibilityClassification.EXACT
    assert assessment.is_executable is True


def test_registry_rejects_duplicate_normalized_patterns() -> None:
    registry = NumericCompatibilityRegistry()
    pattern = CompatibilityRulePattern(model_family="affine_regression")
    registry.register(_rule("first", pattern))

    with pytest.raises(DuplicateCompatibilityRuleError):
        registry.register(_rule("second", pattern))


def test_registry_fails_closed_on_equally_specific_overlapping_rules() -> None:
    registry = NumericCompatibilityRegistry()
    registry.register(
        _rule(
            "framework-model",
            CompatibilityRulePattern(
                framework_adapter_id="framework",
                model_family="affine_regression",
            ),
        )
    )
    registry.register(
        _rule(
            "encoder-backend",
            CompatibilityRulePattern(
                model_encoder_id="affine-encoder",
                backend_kind=BackendKind.SMT.value,
            ),
        )
    )

    with pytest.raises(AmbiguousCompatibilityRuleError):
        registry.assess(_query(), backend_profile=_backend_profile())


def test_registry_defaults_an_unmatched_route_to_unknown() -> None:
    assessment = NumericCompatibilityRegistry().assess(
        _query(), backend_profile=_backend_profile()
    )

    assert assessment.matched_rule_id is None
    assert assessment.classification is CompatibilityClassification.UNKNOWN
    assert assessment.support_status is SupportStatus.UNSUPPORTED
    assert assessment.is_executable is False


def test_registry_rejects_non_finite_values_before_rule_matching() -> None:
    registry = NumericCompatibilityRegistry()
    registry.register(_rule("generic", CompatibilityRulePattern()))

    assessment = registry.assess(
        _query(non_finite=True), backend_profile=_backend_profile()
    )

    assert assessment.classification is CompatibilityClassification.INCOMPATIBLE
    assert assessment.is_executable is False
    assert "NaN or infinity" in assessment.diagnostics[0]


def test_registry_normalizes_identity_case_and_whitespace() -> None:
    registry = NumericCompatibilityRegistry()
    registry.register(
        _rule(
            " Normalized.Rule ",
            CompatibilityRulePattern(
                framework_adapter_id=" Framework ",
                backend_kind=" SMT ",
                required_property_tags=frozenset({" AFFINE_ARITHMETIC "}),
            ),
        )
    )

    assessment = registry.assess(_query(), backend_profile=_backend_profile())

    assert assessment.matched_rule_id == "normalized.rule"


def test_registry_rejects_duplicates_after_identity_normalization() -> None:
    registry = NumericCompatibilityRegistry()
    registry.register(
        _rule(
            "first",
            CompatibilityRulePattern(framework_adapter_id="Framework"),
        )
    )

    with pytest.raises(DuplicateCompatibilityRuleError):
        registry.register(
            _rule(
                "second",
                CompatibilityRulePattern(framework_adapter_id=" framework "),
            )
        )
