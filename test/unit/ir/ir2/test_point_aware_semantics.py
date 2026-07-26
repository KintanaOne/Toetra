from __future__ import annotations

from toetra._compiler.ir.ir1.nodes import AndIR, ComparisonIR, NotIR
from toetra._compiler.ir.ir2.enums import VerificationSemantics
from toetra._compiler.ir.ir2.nodes import NNFFormulaIR2
from test.unit.ir.ir2._point_aware_helpers import compile_ir2


def test_ir2_sem_001_universal_pairwise_uses_refutation_body() -> None:
    task = compile_ir2("""
        model := "credit_risk.joblib"
        target := RiskScore

        [MONOTONICITY]:
        forall lower, higher
        where higher.income >= lower.income
        => target[higher] <= target[lower]
        """)
    assert task.semantics is VerificationSemantics.REFUTATION
    assert task.requirements.binder_sequence == ("forall", "forall")
    assert task.requirements.requires_native_quantifiers is False
    condition = task.verification_condition
    assert isinstance(condition, NNFFormulaIR2)
    assert isinstance(condition.expression, AndIR)
    restriction, negated_property = condition.expression.operands
    assert isinstance(restriction, ComparisonIR)
    assert isinstance(negated_property, NotIR)
    assert isinstance(negated_property.operand, ComparisonIR)


def test_ir2_sem_002_existential_pair_search_uses_satisfaction_body() -> None:
    task = compile_ir2("""
        model := "credit_risk.joblib"
        target := RiskScore

        [LOGIC]:
        exists candidate, reference
        where candidate.income >= reference.income
        => target[candidate] <= target[reference]
        """)
    assert task.semantics is VerificationSemantics.SATISFACTION
    assert task.requirements.binder_sequence == ("exists", "exists")
    assert task.requirements.requires_native_quantifiers is False
    condition = task.verification_condition
    assert isinstance(condition, NNFFormulaIR2)
    assert isinstance(condition.expression, AndIR)
    restriction, property_expression = condition.expression.operands
    assert isinstance(restriction, ComparisonIR)
    assert isinstance(property_expression, ComparisonIR)
