from __future__ import annotations

from toetra._compiler.ast.nodes.expressions import AtExprNode, CheckAtExprNode
from toetra._compiler.ast.nodes.neighborhood import NeighborhoodMembershipNode
from tests.support.program_builder import build_program


def test_ast_chk_001_check_at_preserves_selection_and_source_span() -> None:
    scope = (
        build_program(
            declarations="anchor x0 := { age: 42 }",
            body="check_at x0 => target <= 7",
            property_type="BOUND",
        )
        .body[0]
        .rule.scope
    )

    assert isinstance(scope, CheckAtExprNode)
    assert scope.variable == "x0"
    assert scope.source_span is not None
    assert scope.source_span.line > 0


def test_ast_at_001_local_sugar_preserves_both_points_and_source_span() -> None:
    scope = (
        build_program(
            declarations="anchor x0 := { age: 42 }",
            body="""
        at x0 with x1 in neighborhood(metric = Linf, eps = 0.05)
        => target[x1] >= target[x0]
        """,
            property_type="ROBUSTNESS",
        )
        .body[0]
        .rule.scope
    )

    assert isinstance(scope, AtExprNode)
    assert scope.variable == "x0"
    assert isinstance(scope.local_membership, NeighborhoodMembershipNode)
    assert scope.local_membership.anchor == "x0"
    assert scope.local_membership.candidate == "x1"
    assert scope.local_membership.metric == "Linf"
    assert scope.source_span is not None
    assert scope.local_membership.source_span is not None
