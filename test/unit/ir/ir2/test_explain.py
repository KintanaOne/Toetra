from dsl.ir.ir1.nodes import (
    AttributeExpressionIR,
    ComparisonIR,
    ConstantExpressionIR,
    ScopeIR,
)
from dsl.ir.ir2.enums import (
    AssumptionSource,
    NormalFormKind,
    VerificationSemantics,
)
from dsl.ir.ir2.explain import IR2ExplainOptions, explain_ir2_task
from dsl.ir.ir2.guardrails.diagnostics import (
    DiagnosticSeverity,
    IR2Diagnostic,
)
from dsl.ir.ir2.nodes import AssumptionIR2, NNFFormulaIR2, VerificationTaskIR2
from dsl.ir.ir2.requirements import IR2Requirements
from dsl.language.vocabulary.operators import EnumComparisonOperator
from dsl.language.vocabulary.properties import EnumProperty
from dsl.semantic.types.enums import EnumDataType


def _comparison(feature: str, value: int) -> ComparisonIR:
    return ComparisonIR(
        left=AttributeExpressionIR(entity="_x", feature=feature),
        op=EnumComparisonOperator.LTE,
        right=ConstantExpressionIR(value=value, dtype=EnumDataType.INT),
    )


def _task() -> VerificationTaskIR2:
    spec = NNFFormulaIR2(expression=_comparison("a", 1))
    assumption = AssumptionIR2(
        source=AssumptionSource.MODEL,
        formula=NNFFormulaIR2(expression=_comparison("model_score", 0)),
        description="fake model assumption",
        metadata={"encoder": "fake"},
    )

    return VerificationTaskIR2(
        property_type=EnumProperty.LOGIC,
        scope=ScopeIR(
            kind="quantifier",
            variables={"_x": "symbolic"},
            neighborhood=None,
            domain=None,
        ),
        backend=None,
        assumptions=(assumption,),
        spec_formula=spec,
        verification_condition=spec,
        semantics=VerificationSemantics.REFUTATION,
        normal_form=NormalFormKind.NNF,
        requirements=IR2Requirements(
            requires_boolean_logic=True,
            requires_numeric_comparisons=True,
            requires_problem_predicates=False,
            requires_model_assertions=True,
            requires_native_quantifiers=True,
            requires_domains=False,
            requires_neighborhoods=False,
            normal_form=NormalFormKind.NNF,
            requires_affine_arithmetic=True,
            requires_domain_assumptions=True,
            required_scalar_sorts=frozenset({EnumDataType.FLOAT}),
        ),
        diagnostics=(
            IR2Diagnostic(
                code="IR2_TEST_WARNING",
                severity=DiagnosticSeverity.WARNING,
                message="test diagnostic",
            ),
        ),
    )


def test_explain_ir2_task_shows_intersection_between_spec_assumptions_and_vc():
    text = explain_ir2_task(_task())

    assert "IR2 Explanation" in text
    assert "User specification P" in text
    assert "Assumptions Γ" in text
    assert "Verification condition" in text
    assert "VC = Γ ∧ ¬P" in text
    assert "fake model assumption" in text
    assert "model_assertions: True" in text
    assert "affine_arithmetic: True" in text
    assert "domain_assumptions: True" in text
    assert "scalar_sorts: float" in text
    assert "IR2_TEST_WARNING" in text


def test_explain_ir2_task_can_include_mermaid_view():
    text = explain_ir2_task(
        _task(),
        options=IR2ExplainOptions(include_mermaid=True),
    )

    assert "```mermaid" in text
    assert "DSL spec P" in text
    assert "Γ assumptions (1)" in text
    assert "Backend routing" in text
