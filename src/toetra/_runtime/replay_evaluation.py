from __future__ import annotations

import math
from typing import Any, Mapping

from toetra._compiler.ir.ir1.model_quantities import ModelQuantityExpressionIR
from toetra._compiler.ir.ir1.nodes import (
    AndIR,
    AttributeExpressionIR,
    BinaryArithmeticExpressionIR,
    ComparisonIR,
    ConstantExpressionIR,
    ImplyIR,
    LogicalIR,
    NotIR,
    OrIR,
    ScalarExpressionIR,
    TargetExpressionIR,
    UnaryArithmeticExpressionIR,
)
from toetra._compiler.ir.ir1.outputs import OutputObservableExpressionIR
from toetra._runtime.errors import ReplayUnavailableError
from toetra._runtime.model_observer import ModelObservation
from toetra._models.schema.output_schema import EnumOutputObservable


def evaluate_logical(
    node: LogicalIR,
    inputs: Mapping[str, Mapping[str, Any]],
    observations: Mapping[str, ModelObservation],
    *,
    tolerance: float,
) -> bool | None:
    """Evaluate preserved logic with a three-valued numeric boundary policy.

    Numeric ordering comparisons that land inside ``tolerance`` of their
    boundary return ``None``. This prevents an exact-real Z3 witness from being
    rejected solely because its concrete IEEE-754 replay rounded to the other
    side of a strict or non-strict boundary.
    """

    if isinstance(node, ComparisonIR):
        left = _evaluate_scalar(node.left, inputs, observations)
        right = _evaluate_scalar(node.right, inputs, observations)
        return _evaluate_comparison(
            left,
            node.op.value,
            right,
            tolerance=tolerance,
        )
    if isinstance(node, AndIR):
        return _truth_and(
            tuple(
                evaluate_logical(
                    item,
                    inputs,
                    observations,
                    tolerance=tolerance,
                )
                for item in node.operands
            )
        )
    if isinstance(node, OrIR):
        return _truth_or(
            tuple(
                evaluate_logical(
                    item,
                    inputs,
                    observations,
                    tolerance=tolerance,
                )
                for item in node.operands
            )
        )
    if isinstance(node, NotIR):
        return _truth_not(
            evaluate_logical(
                node.operand,
                inputs,
                observations,
                tolerance=tolerance,
            )
        )
    if isinstance(node, ImplyIR):
        left = evaluate_logical(
            node.left,
            inputs,
            observations,
            tolerance=tolerance,
        )
        right = evaluate_logical(
            node.right,
            inputs,
            observations,
            tolerance=tolerance,
        )
        return _truth_or((_truth_not(left), right))
    raise ReplayUnavailableError(
        f"Replay cannot evaluate logical node {type(node).__name__}"
    )


def _evaluate_comparison(
    left: Any,
    operator: str,
    right: Any,
    *,
    tolerance: float,
) -> bool | None:
    numeric_values = _finite_numeric_pair(left, right)
    if numeric_values is None:
        return {
            "==": left == right,
            "!=": left != right,
            "<": left < right,
            "<=": left <= right,
            ">": left > right,
            ">=": left >= right,
        }[operator]

    numeric_left, numeric_right = numeric_values
    distance = abs(numeric_left - numeric_right)
    if operator == "==":
        return distance <= tolerance
    if operator == "!=":
        return distance > tolerance
    if tolerance > 0 and distance <= tolerance:
        return None
    return {
        "<": numeric_left < numeric_right,
        "<=": numeric_left <= numeric_right,
        ">": numeric_left > numeric_right,
        ">=": numeric_left >= numeric_right,
    }[operator]


def _finite_numeric_pair(left: Any, right: Any) -> tuple[float, float] | None:
    try:
        numeric_left = float(left)
        numeric_right = float(right)
    except (TypeError, ValueError, OverflowError):
        return None
    if not math.isfinite(numeric_left) or not math.isfinite(numeric_right):
        return None
    return numeric_left, numeric_right


def _truth_not(value: bool | None) -> bool | None:
    return None if value is None else not value


def _truth_and(values: tuple[bool | None, ...]) -> bool | None:
    if any(value is False for value in values):
        return False
    if any(value is None for value in values):
        return None
    return True


def _truth_or(values: tuple[bool | None, ...]) -> bool | None:
    if any(value is True for value in values):
        return True
    if any(value is None for value in values):
        return None
    return False


def _evaluate_scalar(
    node: ScalarExpressionIR,
    inputs: Mapping[str, Mapping[str, Any]],
    observations: Mapping[str, ModelObservation],
) -> Any:
    if isinstance(node, ConstantExpressionIR):
        return node.value
    if isinstance(node, AttributeExpressionIR):
        point_name = node.point.name if node.point is not None else node.entity
        try:
            return inputs[point_name][node.feature]
        except KeyError as error:
            raise ReplayUnavailableError(
                f"Replay value missing for {point_name}.{node.feature}"
            ) from error
    if isinstance(node, TargetExpressionIR):
        if node.evaluation is None:
            raise ReplayUnavailableError(
                "Replay target has no point evaluation identity"
            )
        observation = _observation_for(node.evaluation.point.name, observations)
        if observation.regression_value is None:
            raise ReplayUnavailableError(
                f"Replay output missing for {node.evaluation.output_name!r}"
            )
        return observation.regression_value
    if isinstance(node, OutputObservableExpressionIR):
        observation = _observation_for(node.evaluation.point.name, observations)
        if node.observable is EnumOutputObservable.PREDICTED_LABEL:
            if observation.predicted_label is None:
                raise ReplayUnavailableError("Replay predicted label is unavailable")
            return observation.predicted_label
        if node.observable is EnumOutputObservable.CLASS_PROBABILITY:
            if node.label is None:
                raise ReplayUnavailableError(
                    "Replay class-probability observable has no label selector"
                )
            try:
                return observation.class_probabilities[node.label.value]
            except KeyError as error:
                raise ReplayUnavailableError(
                    f"Replay probability missing for label {node.label.value!r}"
                ) from error
    if isinstance(node, ModelQuantityExpressionIR):
        observation = _observation_for(node.evaluation.point.name, observations)
        try:
            return observation.model_quantities[node.quantity_kind.value]
        except KeyError as error:
            raise ReplayUnavailableError(
                f"Replay model quantity missing: {node.quantity_kind.value}"
            ) from error
    if isinstance(node, UnaryArithmeticExpressionIR):
        value = _evaluate_scalar(node.operand, inputs, observations)
        return -value if node.operator.value == "-" else +value
    if isinstance(node, BinaryArithmeticExpressionIR):
        left = _evaluate_scalar(node.left, inputs, observations)
        right = _evaluate_scalar(node.right, inputs, observations)
        return {
            "+": lambda: left + right,
            "-": lambda: left - right,
            "*": lambda: left * right,
            "/": lambda: left / right,
        }[node.operator.value]()
    raise ReplayUnavailableError(
        f"Replay cannot evaluate scalar node {type(node).__name__}"
    )


def _observation_for(
    point_name: str,
    observations: Mapping[str, ModelObservation],
) -> ModelObservation:
    try:
        return observations[point_name]
    except KeyError as error:
        raise ReplayUnavailableError(
            f"Replay observation missing for point {point_name!r}"
        ) from error


def absolute_error(left: Any, right: Any) -> float | None:
    if right is None:
        return None
    try:
        return abs(float(left) - float(right))
    except (TypeError, ValueError):
        return 0.0 if left == right else None
