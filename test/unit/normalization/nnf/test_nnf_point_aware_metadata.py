from __future__ import annotations

from dsl.ir.ir1.nodes import ComparisonIR, ImplyIR, OrIR, TargetExpressionIR
from dsl.ir.ir1.run_ir1 import run_ir
from dsl.ir.normalization.nnf import NNFNormalizer


def test_nnf_preserves_binder_point_and_evaluation_identity() -> None:
    task = run_ir("""
        model := "credit.joblib"
        target := score

        [LOGIC]:
        forall x0, x1
        where x1.income >= x0.income
        => target[x1] <= target[x0]
        """)[0]

    before = task.query.expression
    assert isinstance(before, ImplyIR)
    before_comparison = before.right
    assert isinstance(before_comparison, ComparisonIR)
    assert isinstance(before_comparison.left, TargetExpressionIR)
    left_evaluation = before_comparison.left.evaluation
    assert task.scope.restriction is not None

    normalized = NNFNormalizer().normalize_task(task)

    assert normalized.scope.points == task.scope.points
    assert normalized.scope.binders == task.scope.binders
    assert normalized.scope.restriction is not None
    assert normalized.scope.restriction.provenance == task.scope.restriction.provenance
    assert isinstance(normalized.query.expression, OrIR)

    normalized_comparison = normalized.query.expression.operands[1]
    assert isinstance(normalized_comparison, ComparisonIR)
    assert isinstance(normalized_comparison.left, TargetExpressionIR)
    assert normalized_comparison.left.evaluation is left_evaluation
