from __future__ import annotations

from toetra._compiler.ir.ir1.nodes import AndIR, ComparisonIR, ImplyIR
from toetra._compiler.ir.ir1.run_ir1 import run_ir


def test_ir1_rst_001_where_is_preserved_separately_from_language_formula() -> None:
    task = run_ir("""
        model := "credit.joblib"
        target := score

        [MONOTONICITY]:
        forall lower, higher
        where higher.income >= lower.income
        => target[higher] <= target[lower]
        """)[0]

    assert task.scope.restriction is not None
    assert task.scope.restriction.provenance.origin == "where"
    assert isinstance(task.scope.restriction.expression, ComparisonIR)
    assert isinstance(task.query.expression, ImplyIR)
    assert task.query.expression.left == task.scope.restriction.expression


def test_existential_where_keeps_restriction_and_conjunctive_formula() -> None:
    task = run_ir("""
        model := "credit.joblib"
        target := score

        [LOGIC]:
        exists applicant
        where applicant.debt_ratio >= 0.5
        => target[applicant] >= 0.9
        """)[0]

    assert task.scope.restriction is not None
    assert isinstance(task.query.expression, AndIR)
    assert task.query.expression.operands[0] == task.scope.restriction.expression
