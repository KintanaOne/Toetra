from __future__ import annotations

from dsl.ast.nodes.assertion import ComparisonNode
from dsl.ast.nodes.primitives import TargetRefNode
from test.unit.builder._point_binding_helpers import build_program


def test_ast_tgt_001_indexed_target_stores_point_identifier() -> None:
    comparison = (
        build_program(body="forall x0 => target[x0] <= 7").body[0].rule.assertion.root
    )

    assert isinstance(comparison, ComparisonNode)
    assert comparison.left == TargetRefNode(point="x0")


def test_ast_tgt_002_unindexed_target_has_no_point_identifier() -> None:
    comparison = (
        build_program(body="forall x0 => target <= 7").body[0].rule.assertion.root
    )

    assert isinstance(comparison, ComparisonNode)
    assert comparison.left == TargetRefNode(point=None)
