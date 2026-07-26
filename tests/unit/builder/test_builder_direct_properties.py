from __future__ import annotations

from toetra._compiler.ast.nodes.assertion import ComparisonNode
from toetra._compiler.ast.nodes.expressions import DirectExprNode
from toetra._compiler.ast.nodes.primitives import TargetRefNode
from tests.support.program_builder import build_program


def test_ast_dir_001_direct_property_is_distinct_from_scoped_form() -> None:
    property_node = build_program(
        declarations="anchor x0 := { age: 42 }",
        body="target[x0] <= 0.4 using Z3",
        property_type="BOUND",
    ).body[0]

    assert isinstance(property_node.rule.scope, DirectExprNode)
    assert isinstance(property_node.rule.assertion.root, ComparisonNode)
    assert property_node.rule.assertion.root.left == TargetRefNode(point="x0")
