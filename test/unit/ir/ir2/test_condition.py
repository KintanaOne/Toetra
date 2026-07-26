from __future__ import annotations

from toetra._compiler.ir.ir1.nodes import (
    AndIR,
    AttributeExpressionIR,
    ComparisonIR,
    ConstantExpressionIR,
    NotIR,
)
from toetra._compiler.ir.ir2.condition import VerificationConditionBuilder
from toetra._compiler.ir.ir2.enums import AssumptionSource, VerificationSemantics
from toetra._compiler.ir.ir2.dsl.nodes import (
    AssumptionIR2,
    NNFFormulaIR2,
)
from toetra._language.vocabulary.operators import EnumComparisonOperator
from toetra._compiler.semantic.types.enums import EnumDataType


def _property_atom() -> ComparisonIR:
    return ComparisonIR(
        left=AttributeExpressionIR(entity="x0", feature="a"),
        op=EnumComparisonOperator.LTE,
        right=ConstantExpressionIR(value=3.0, dtype=EnumDataType.FLOAT),
    )


def _domain_atom() -> ComparisonIR:
    return ComparisonIR(
        left=AttributeExpressionIR(entity="x0", feature="a"),
        op=EnumComparisonOperator.GTE,
        right=ConstantExpressionIR(value=0.0, dtype=EnumDataType.FLOAT),
    )


def _domain_assumption() -> AssumptionIR2:
    return AssumptionIR2(
        source=AssumptionSource.DOMAIN,
        formula=NNFFormulaIR2(
            expression=_domain_atom(),
        ),
        description="x0.a lower domain bound",
    )


def test_build_refutation_condition_without_assumptions_negates_property():
    property_atom = _property_atom()
    spec_formula = NNFFormulaIR2(expression=property_atom)

    condition = VerificationConditionBuilder().build_condition(
        spec_formula,
        semantics=VerificationSemantics.REFUTATION,
    )

    expression = condition.expression

    assert isinstance(expression, NotIR)
    assert expression.operand == property_atom


def test_build_refutation_condition_with_assumptions_builds_gamma_and_not_property():
    property_atom = _property_atom()
    assumption = _domain_assumption()

    condition = VerificationConditionBuilder().build_condition(
        NNFFormulaIR2(expression=property_atom),
        assumptions=(assumption,),
        semantics=VerificationSemantics.REFUTATION,
    )

    expression = condition.expression

    assert isinstance(expression, AndIR)
    assert len(expression.operands) == 2

    gamma_expression = expression.operands[0]
    property_expression = expression.operands[1]

    assert gamma_expression == assumption.formula.expression
    assert isinstance(property_expression, NotIR)
    assert property_expression.operand == property_atom


def test_build_satisfaction_condition_without_assumptions_preserves_property():
    property_atom = _property_atom()
    spec_formula = NNFFormulaIR2(expression=property_atom)

    condition = VerificationConditionBuilder().build_condition(
        spec_formula,
        semantics=VerificationSemantics.SATISFACTION,
    )

    assert condition.expression == property_atom
    assert not isinstance(condition.expression, NotIR)


def test_build_satisfaction_condition_with_assumptions_builds_gamma_and_property():
    property_atom = _property_atom()
    assumption = _domain_assumption()

    condition = VerificationConditionBuilder().build_condition(
        NNFFormulaIR2(expression=property_atom),
        assumptions=(assumption,),
        semantics=VerificationSemantics.SATISFACTION,
    )

    expression = condition.expression

    assert isinstance(expression, AndIR)
    assert len(expression.operands) == 2

    gamma_expression = expression.operands[0]
    property_expression = expression.operands[1]

    assert gamma_expression == assumption.formula.expression
    assert property_expression == property_atom
    assert not isinstance(property_expression, NotIR)


def test_refutation_wrapper_uses_refutation_semantics():
    property_atom = _property_atom()

    condition = VerificationConditionBuilder().build_refutation_condition(
        NNFFormulaIR2(expression=property_atom),
    )

    assert isinstance(condition.expression, NotIR)
    assert condition.expression.operand == property_atom


def test_satisfaction_wrapper_uses_satisfaction_semantics():
    property_atom = _property_atom()

    condition = VerificationConditionBuilder().build_satisfaction_condition(
        NNFFormulaIR2(expression=property_atom),
    )

    assert condition.expression == property_atom
    assert not isinstance(condition.expression, NotIR)
