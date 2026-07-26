from __future__ import annotations

from toetra._compiler.ir.ir1.nodes import AttributeExpressionIR, ComparisonIR
from toetra._compiler.ir.ir1.run_ir1 import run_ir


def test_domain_and_feature_references_reuse_exact_point_identity() -> None:
    task = run_ir("""
        model := "credit.joblib"
        target := score

        [BOUND]:
        forall applicant
        with domain(applicant.age: [18, 90])
        => applicant.age >= 18
        """)[0]

    assert task.scope.domain is not None
    domain_entry = task.scope.domain.entries[0]
    comparison = task.query.expression
    assert isinstance(comparison, ComparisonIR)
    assert isinstance(comparison.left, AttributeExpressionIR)
    assert domain_entry.point is task.scope.points[0]
    assert comparison.left.point is task.scope.points[0]
