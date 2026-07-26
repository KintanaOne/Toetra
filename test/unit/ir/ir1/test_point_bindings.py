from __future__ import annotations

from toetra._compiler.ir.ir1.nodes import ComparisonIR, TargetExpressionIR
from toetra._compiler.ir.ir1.run_ir1 import run_ir


def test_ir1_pnt_001_two_points_keep_distinct_stable_identities() -> None:
    task = run_ir("""
        model := "credit.joblib"
        target := score

        [LOGIC]:
        forall x0, x1 => target[x0] <= target[x1]
        """)[0]

    assert [point.name for point in task.scope.points] == ["x0", "x1"]
    assert task.scope.points[0] is not task.scope.points[1]

    comparison = task.query.expression
    assert isinstance(comparison, ComparisonIR)
    assert isinstance(comparison.left, TargetExpressionIR)
    assert isinstance(comparison.right, TargetExpressionIR)
    assert comparison.left.point is task.scope.points[0]
    assert comparison.right.point is task.scope.points[1]


def test_ir1_qp_001_homogeneous_binder_chain_preserves_order_and_kind() -> None:
    task = run_ir("""
        model := "credit.joblib"
        target := score

        [LOGIC]:
        forall x0, x1
        forall x2
        => target[x0] <= target[x2]
        """)[0]

    assert [binder.quantifier for binder in task.scope.binders] == [
        "forall",
        "forall",
        "forall",
    ]
    assert [binder.point.name for binder in task.scope.binders] == [
        "x0",
        "x1",
        "x2",
    ]
    assert [binder.point.binding_kind for binder in task.scope.binders] == [
        "universal",
        "universal",
        "universal",
    ]
    assert task.scope.quantifier == "forall"


def test_ir1_qp_002_alternating_binder_chain_is_not_flattened() -> None:
    task = run_ir("""
        model := "credit.joblib"
        target := score

        [LOGIC]:
        forall original
        exists counterfactual
        => target[counterfactual] <= target[original]
        """)[0]

    assert [binder.quantifier for binder in task.scope.binders] == [
        "forall",
        "exists",
    ]
    assert [binder.point.name for binder in task.scope.binders] == [
        "original",
        "counterfactual",
    ]
    assert [binder.point.binding_kind for binder in task.scope.binders] == [
        "universal",
        "existential",
    ]
    assert task.scope.quantifier is None
