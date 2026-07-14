from __future__ import annotations

from collections.abc import Iterator

from dsl.ir.ir1.nodes import (
    AttributeExpressionIR,
    BinaryArithmeticExpressionIR,
    ConstantExpressionIR,
    ScalarExpressionIR,
    SymbolLiteralIR,
    TargetExpressionIR,
    UnaryArithmeticExpressionIR,
)
from dsl.language.vocabulary.operators import EnumArithmeticOperator


def iter_scalar_expressions(node: ScalarExpressionIR) -> Iterator[ScalarExpressionIR]:
    """Yield a scalar expression tree in pre-order."""
    yield node

    if isinstance(node, UnaryArithmeticExpressionIR):
        yield from iter_scalar_expressions(node.operand)
        return

    if isinstance(node, BinaryArithmeticExpressionIR):
        yield from iter_scalar_expressions(node.left)
        yield from iter_scalar_expressions(node.right)


def references_model_output(node: ScalarExpressionIR) -> bool:
    return any(
        isinstance(item, TargetExpressionIR) and item.entity == "_model"
        for item in iter_scalar_expressions(node)
    )


def format_scalar_expression(node: ScalarExpressionIR) -> str:
    """Render a scalar tree while preserving operator precedence and shape."""
    return _format(node, parent_precedence=0, is_right_child=False)


def _format(
    node: ScalarExpressionIR,
    *,
    parent_precedence: int,
    is_right_child: bool,
) -> str:
    precedence = _precedence(node)

    if isinstance(node, ConstantExpressionIR):
        text = repr(node.value)
    elif isinstance(node, AttributeExpressionIR):
        text = f"{node.entity}.{node.feature}"
    elif isinstance(node, SymbolLiteralIR):
        text = node.name
    elif isinstance(node, TargetExpressionIR):
        text = f"{node.entity}.{node.feature}"
    elif isinstance(node, UnaryArithmeticExpressionIR):
        operand = _format(
            node.operand,
            parent_precedence=precedence,
            is_right_child=True,
        )
        text = f"{node.operator.value}{operand}"
    elif isinstance(node, BinaryArithmeticExpressionIR):
        left = _format(
            node.left,
            parent_precedence=precedence,
            is_right_child=False,
        )
        right = _format(
            node.right,
            parent_precedence=precedence,
            is_right_child=True,
        )
        text = f"{left} {node.operator.value} {right}"
    else:
        raise TypeError(f"Unsupported scalar IR node: {type(node).__name__}")

    needs_parentheses = precedence < parent_precedence
    if is_right_child and precedence == parent_precedence:
        needs_parentheses = isinstance(
            node,
            (BinaryArithmeticExpressionIR, UnaryArithmeticExpressionIR),
        )

    return f"({text})" if needs_parentheses else text


def _precedence(node: ScalarExpressionIR) -> int:
    if isinstance(node, BinaryArithmeticExpressionIR):
        if node.operator in {
            EnumArithmeticOperator.MUL,
            EnumArithmeticOperator.DIV,
        }:
            return 20
        return 10

    if isinstance(node, UnaryArithmeticExpressionIR):
        return 30

    return 40
