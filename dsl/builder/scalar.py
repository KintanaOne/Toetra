from __future__ import annotations

from lark import Tree

from dsl.ast.nodes.primitives import ScalarExpressionNode, TargetRefNode
from dsl.builder.core.ast_utils import parse_attribute, parse_value


_SINGLE_CHILD_WRAPPERS = {
    "scalar_expression",
    "additive_expr",
    "multiplicative_expr",
    "unary_expr",
    "scalar_primary",
    "parenthesized_scalar",
}

_OPERATOR_RULES = {
    "additive_operator",
    "multiplicative_operator",
    "unary_operator",
}


def _tree_children(node: Tree) -> list[Tree]:
    return [child for child in node.children if isinstance(child, Tree)]


def parse_scalar_expression(node: Tree) -> ScalarExpressionNode:
    """Build the leaf subset of the scalar-expression AST.

    G2-A intentionally supports constants, attributes, target references, and
    parenthesized leaf expressions. Arithmetic operators are parsed by G1 but
    remain a later builder sub-gate.
    """

    rule = str(node.data)

    if rule == "value":
        return parse_value(node)

    if rule == "attribute":
        return parse_attribute(node)

    if rule == "target_ref":
        return TargetRefNode()

    if rule in _SINGLE_CHILD_WRAPPERS:
        children = _tree_children(node)
        operator_children = [
            child for child in children if str(child.data) in _OPERATOR_RULES
        ]

        if operator_children or len(children) != 1:
            raise NotImplementedError(
                "Arithmetic scalar expressions are not implemented in G2-A."
            )

        return parse_scalar_expression(children[0])

    raise ValueError(f"Unsupported scalar-expression node: {rule}")
