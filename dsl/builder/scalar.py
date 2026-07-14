from __future__ import annotations

from lark import Tree

from dsl.ast.nodes.primitives import (
    BinaryArithmeticNode,
    NameRefNode,
    ScalarExpressionNode,
    TargetRefNode,
    UnaryArithmeticNode,
)
from dsl.builder.core.ast_utils import parse_attribute, parse_value
from dsl.builder.core.utils import get_token_value
from dsl.language.vocabulary.operators import (
    EnumArithmeticOperator,
    EnumUnaryOperator,
)


def _tree_children(node: Tree) -> list[Tree]:
    return [child for child in node.children if isinstance(child, Tree)]


def _operator_value(node: Tree) -> str:
    value = get_token_value(node)

    if value is None:
        raise ValueError(f"Missing operator value in {node.data}")

    return value


def _parse_left_associative(
    node: Tree,
    *,
    operand_rule: str,
    operator_rule: str,
) -> ScalarExpressionNode:
    """Build a left-associative arithmetic chain from one CST level."""
    children = _tree_children(node)

    if not children or str(children[0].data) != operand_rule:
        raise ValueError(f"Invalid {node.data} expression")

    expression = parse_scalar_expression(children[0])
    index = 1

    while index < len(children):
        operator_node = children[index]

        if str(operator_node.data) != operator_rule or index + 1 >= len(children):
            raise ValueError(f"Invalid {node.data} operator sequence")

        right_node = children[index + 1]
        if str(right_node.data) != operand_rule:
            raise ValueError(f"Invalid {node.data} right operand")

        expression = BinaryArithmeticNode(
            left=expression,
            operator=EnumArithmeticOperator(_operator_value(operator_node)),
            right=parse_scalar_expression(right_node),
        )
        index += 2

    return expression


def parse_scalar_expression(node: Tree) -> ScalarExpressionNode:
    """Build a complete scalar-expression AST while preserving precedence."""
    rule = str(node.data)

    if rule == "value":
        return parse_value(node)

    if rule == "attribute":
        attribute = parse_attribute(node)

        if attribute.entity is None:
            return NameRefNode(name=attribute.feature)

        return attribute

    if rule == "target_ref":
        return TargetRefNode()

    if rule == "scalar_expression":
        children = _tree_children(node)
        if len(children) != 1:
            raise ValueError("Scalar expression requires exactly one additive child")
        return parse_scalar_expression(children[0])

    if rule == "additive_expr":
        return _parse_left_associative(
            node,
            operand_rule="multiplicative_expr",
            operator_rule="additive_operator",
        )

    if rule == "multiplicative_expr":
        return _parse_left_associative(
            node,
            operand_rule="unary_expr",
            operator_rule="multiplicative_operator",
        )

    if rule == "unary_expr":
        children = _tree_children(node)

        if len(children) == 1:
            return parse_scalar_expression(children[0])

        if (
            len(children) == 2
            and str(children[0].data) == "unary_operator"
            and str(children[1].data) == "unary_expr"
        ):
            return UnaryArithmeticNode(
                operator=EnumUnaryOperator(_operator_value(children[0])),
                operand=parse_scalar_expression(children[1]),
            )

        raise ValueError("Invalid unary expression")

    if rule in {"scalar_primary", "parenthesized_scalar"}:
        children = _tree_children(node)
        if len(children) != 1:
            raise ValueError(f"Invalid {rule} expression")
        return parse_scalar_expression(children[0])

    raise ValueError(f"Unsupported scalar-expression node: {rule}")
