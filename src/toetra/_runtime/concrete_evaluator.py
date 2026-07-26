from __future__ import annotations

from typing import Any, Mapping

from toetra._compiler.ir.ir1.nodes import (
    AndIR,
    AttributeExpressionIR,
    BinaryArithmeticExpressionIR,
    ComparisonIR,
    ConstantExpressionIR,
    LogicalIR,
    NotIR,
    OrIR,
    ScalarExpressionIR,
    SymbolLiteralIR,
    TargetExpressionIR,
    UnaryArithmeticExpressionIR,
)
from toetra._language.vocabulary.operators import (
    EnumArithmeticOperator,
    EnumComparisonOperator,
    EnumUnaryOperator,
)


def evaluate_logical_expression(
    node: LogicalIR,
    *,
    point_values: Mapping[str, Mapping[str, Any]],
    output_values: Mapping[str, Mapping[str, Any]],
) -> bool:
    """Evaluate the supported concrete IR1 subset used by replay."""

    if isinstance(node, ComparisonIR):
        left = evaluate_scalar_expression(
            node.left,
            point_values=point_values,
            output_values=output_values,
        )
        right = evaluate_scalar_expression(
            node.right,
            point_values=point_values,
            output_values=output_values,
        )
        return _compare(left, right, node.op)
    if isinstance(node, AndIR):
        return all(
            evaluate_logical_expression(
                operand,
                point_values=point_values,
                output_values=output_values,
            )
            for operand in node.operands
        )
    if isinstance(node, OrIR):
        return any(
            evaluate_logical_expression(
                operand,
                point_values=point_values,
                output_values=output_values,
            )
            for operand in node.operands
        )
    if isinstance(node, NotIR):
        return not evaluate_logical_expression(
            node.operand,
            point_values=point_values,
            output_values=output_values,
        )
    raise TypeError(
        "Concrete replay cannot evaluate logical node " f"{type(node).__name__}"
    )


def evaluate_scalar_expression(
    node: ScalarExpressionIR,
    *,
    point_values: Mapping[str, Mapping[str, Any]],
    output_values: Mapping[str, Mapping[str, Any]],
) -> Any:
    if isinstance(node, ConstantExpressionIR):
        return node.value
    if isinstance(node, AttributeExpressionIR):
        point_name = node.point.name if node.point is not None else node.entity
        return point_values[point_name][node.feature]
    if isinstance(node, TargetExpressionIR):
        if node.point is None:
            if len(output_values) != 1:
                raise KeyError("Ambiguous concrete target without a point")
            point_name = next(iter(output_values))
        else:
            point_name = node.point.name
        return output_values[point_name][node.feature]
    if isinstance(node, SymbolLiteralIR):
        raise KeyError(f"Unresolved symbolic literal {node.name!r} during replay")
    if isinstance(node, UnaryArithmeticExpressionIR):
        value = evaluate_scalar_expression(
            node.operand,
            point_values=point_values,
            output_values=output_values,
        )
        if node.operator is EnumUnaryOperator.PLUS:
            return +value
        if node.operator is EnumUnaryOperator.MINUS:
            return -value
    if isinstance(node, BinaryArithmeticExpressionIR):
        left = evaluate_scalar_expression(
            node.left,
            point_values=point_values,
            output_values=output_values,
        )
        right = evaluate_scalar_expression(
            node.right,
            point_values=point_values,
            output_values=output_values,
        )
        operations = {
            EnumArithmeticOperator.ADD: lambda: left + right,
            EnumArithmeticOperator.SUB: lambda: left - right,
            EnumArithmeticOperator.MUL: lambda: left * right,
            EnumArithmeticOperator.DIV: lambda: left / right,
        }
        return operations[node.operator]()
    raise TypeError(
        "Concrete replay cannot evaluate scalar node " f"{type(node).__name__}"
    )


def _compare(left: Any, right: Any, operator: EnumComparisonOperator) -> bool:
    comparisons = {
        EnumComparisonOperator.EQ: lambda: left == right,
        EnumComparisonOperator.NEQ: lambda: left != right,
        EnumComparisonOperator.LT: lambda: left < right,
        EnumComparisonOperator.LTE: lambda: left <= right,
        EnumComparisonOperator.GT: lambda: left > right,
        EnumComparisonOperator.GTE: lambda: left >= right,
    }
    return bool(comparisons[operator]())
