from __future__ import annotations

from dsl.ir.ir1.nodes import ComparisonIR, TargetExpressionIR
from dsl.ir.ir1.run_ir1 import run_ir


def test_ir1_tgt_001_indexed_output_keeps_model_point_and_target() -> None:
    task = run_ir("""
        model := "credit_risk.joblib"
        target := RiskScore

        [LOGIC]:
        forall applicant => target[applicant] <= 0.85
        """)[0]

    comparison = task.query.expression
    assert isinstance(comparison, ComparisonIR)
    assert isinstance(comparison.left, TargetExpressionIR)
    assert comparison.left.evaluation is not None
    assert comparison.left.model_identity == "credit_risk.joblib"
    assert comparison.left.point is task.scope.points[0]
    assert comparison.left.evaluation.target_name == "RiskScore"
    assert comparison.left.feature == "RiskScore"
    assert comparison.left.entity == "_model"


def test_repeated_indexed_output_reuses_one_evaluation_identity() -> None:
    task = run_ir("""
        model := "credit_risk.joblib"
        target := RiskScore

        [LOGIC]:
        forall applicant => target[applicant] <= target[applicant]
        """)[0]

    comparison = task.query.expression
    assert isinstance(comparison, ComparisonIR)
    assert isinstance(comparison.left, TargetExpressionIR)
    assert isinstance(comparison.right, TargetExpressionIR)
    assert comparison.left.evaluation is comparison.right.evaluation
