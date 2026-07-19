from __future__ import annotations

from dsl.backends.results import VerificationResult, VerificationStatus
from dsl.backends.router import BackendRoute
from dsl.backends.z3_backend.capabilities import Z3_CAPABILITIES
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
from dsl.ir.ir1.nodes import ComparisonIR, ConstantExpressionIR, ScopeIR
from dsl.ir.ir2.enums import NormalFormKind, VerificationSemantics
from dsl.ir.ir2.nodes import NNFFormulaIR2, VerificationTaskIR2
from dsl.ir.ir2.requirements import IR2Requirements
from dsl.language.vocabulary.backends import EnumBackend
from dsl.language.vocabulary.operators import EnumComparisonOperator
from dsl.language.vocabulary.properties import EnumProperty
from dsl.reporting import build_verification_report
from dsl.semantic.types.enums import EnumDataType


def _assessment() -> NumericCompatibilityAssessment:
    return NumericCompatibilityAssessment(
        query=NumericCompatibilityQuery(
            framework_adapter_id="framework",
            framework_version="2",
            model_family="affine_regression",
            source_execution_profile_id="binary64",
            model_encoder_id="forml.affine-equation",
            model_encoder_version="1",
            backend_kind="smt",
            backend_adapter_id="solver",
            backend_profile_id="exact-real",
            backend_version="4",
            property_numeric_requirements=PropertyNumericRequirements(
                frozenset({"numeric_comparisons", "affine_arithmetic"})
            ),
        ),
        support_status=SupportStatus.SUPPORTED,
        classification=CompatibilityClassification.LOSSY,
        semantic_target="forml.real_affine_extracted_model",
        permitted_conclusions=frozenset(ConclusionKind),
        conclusion_scope=ConclusionScope.SEMANTIC_TARGET_ONLY,
        matched_rule_id="framework-affine-to-exact-real",
        evidence_id="ADR-0018#example",
        assumptions_and_preconditions=("All numeric contributors are finite.",),
        replay_required_for=frozenset(
            {
                ConclusionKind.UNIVERSAL_COUNTEREXAMPLE,
                ConclusionKind.EXISTENTIAL_WITNESS,
            }
        ),
        diagnostics=("The concrete floating execution is not bit-exact.",),
        documentation_reference="docs/adr/ADR-0018.md",
    )


def _task() -> VerificationTaskIR2:
    comparison = ComparisonIR(
        left=ConstantExpressionIR(value=1.0, dtype=EnumDataType.FLOAT),
        op=EnumComparisonOperator.LTE,
        right=ConstantExpressionIR(value=2.0, dtype=EnumDataType.FLOAT),
    )
    formula = NNFFormulaIR2(expression=comparison)
    return VerificationTaskIR2(
        property_type=EnumProperty.LOGIC,
        scope=ScopeIR(
            kind="pointwise",
            variables={"x0": "point"},
            neighborhood=None,
            domain=None,
        ),
        backend=EnumBackend.Z3,
        assumptions=(),
        spec_formula=formula,
        verification_condition=formula,
        semantics=VerificationSemantics.REFUTATION,
        normal_form=NormalFormKind.NNF,
        requirements=IR2Requirements(
            requires_boolean_logic=True,
            requires_numeric_comparisons=True,
            requires_problem_predicates=False,
            requires_model_assertions=False,
            requires_domains=False,
            requires_neighborhoods=False,
            normal_form=NormalFormKind.NNF,
            required_verification_semantics=VerificationSemantics.REFUTATION,
        ),
    )


def _report():
    route = BackendRoute(
        backend=EnumBackend.Z3,
        capabilities=Z3_CAPABILITIES,
        reason="numeric route selected",
        numeric_compatibility=_assessment(),
    )
    result = VerificationResult(
        status=VerificationStatus.PROVED,
        backend=EnumBackend.Z3,
        backend_status="unsat",
        message="proved for the declared semantic target",
    )
    return build_verification_report(_task(), route, result, property_index=0)


def test_builder_preserves_the_complete_numeric_route() -> None:
    compatibility = _report().numeric_compatibility

    assert compatibility is not None
    assert compatibility.matched_rule_id == "framework-affine-to-exact-real"
    assert compatibility.classification == "lossy"
    assert compatibility.semantic_target == "forml.real_affine_extracted_model"
    assert compatibility.conclusion_scope == "semantic_target_only"
    assert compatibility.source_route == "framework@2 / affine_regression / binary64"
    assert compatibility.backend_route == "smt / solver@4 / exact-real"
    assert "applies only to the declared semantic target" in _report().summary
    assert compatibility.property_numeric_requirements == (
        "affine_arithmetic",
        "numeric_comparisons",
    )


def test_json_report_exposes_numeric_compatibility_without_backend_specific_fields() -> (
    None
):
    payload = _report().to_dict()["numeric_compatibility"]

    assert payload["classification"] == "lossy"
    assert payload["semantic_target"] == "forml.real_affine_extracted_model"
    assert payload["source"]["framework_adapter_id"] == "framework"
    assert payload["backend"] == {
        "kind": "smt",
        "adapter_id": "solver",
        "adapter_version": "4",
        "profile_id": "exact-real",
    }
    assert "solver_status" not in payload


def test_text_and_html_reports_make_the_semantic_boundary_visible() -> None:
    report = _report()

    text = report.to_text()
    html = report.to_html()

    assert "Numeric route : lossy (supported)" in text
    assert "Semantic target: forml.real_affine_extracted_model" in text
    assert "Claim scope   : semantic_target_only" in text
    assert "Numeric compatibility" in html
    assert "forml.real_affine_extracted_model" in html
    assert "semantic_target_only" in html
