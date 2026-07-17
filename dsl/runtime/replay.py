from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import Any, Mapping, Protocol, cast

import pandas as pd

from dsl.backends.results import VerificationStatus
from dsl.ir.ir1.nodes import (
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
from dsl.ir.ir2.nodes import VerificationTaskIR2
from dsl.reporting.accessors import point_input_values, point_output_values
from dsl.reporting.model import VerificationReport
from dsl.reporting.values import python_report_value
from dsl.runtime.errors import ReplayUnavailableError
from model.schema.model_schema import ModelSchema


class _Predictor(Protocol):
    def predict(self, values: Any) -> Any: ...


@dataclass(frozen=True)
class PointReplay:
    """Concrete replay evidence for one distinct model-input point."""

    name: str
    inputs: Mapping[str, Any]
    backend_outputs: Mapping[str, Any]
    model_outputs: Mapping[str, Any]
    absolute_errors: Mapping[str, float | None]

    @property
    def is_consistent(self) -> bool:
        return all(error is not None for error in self.absolute_errors.values())


@dataclass(frozen=True)
class CounterexampleReplay:
    """Comparison between formal multi-point evidence and the original model."""

    property_index: int
    points: Mapping[str, PointReplay]
    relation_satisfied: bool | None
    assertion_satisfied: bool | None
    expected_assertion_satisfied: bool | None
    tolerance: float

    @property
    def inputs_by_point(self) -> dict[str, dict[str, Any]]:
        return {name: dict(point.inputs) for name, point in self.points.items()}

    @property
    def backend_outputs_by_point(self) -> dict[str, dict[str, Any]]:
        return {
            name: dict(point.backend_outputs) for name, point in self.points.items()
        }

    @property
    def model_outputs_by_point(self) -> dict[str, dict[str, Any]]:
        return {name: dict(point.model_outputs) for name, point in self.points.items()}

    @property
    def inputs(self) -> dict[str, Any]:
        if len(self.points) != 1:
            raise ValueError("Replay contains multiple points. Use 'inputs_by_point'.")
        return dict(next(iter(self.points.values())).inputs)

    @property
    def backend_outputs(self) -> dict[str, Any]:
        if len(self.points) != 1:
            raise ValueError(
                "Replay contains multiple evaluations. Use 'backend_outputs_by_point'."
            )
        return dict(next(iter(self.points.values())).backend_outputs)

    @property
    def model_outputs(self) -> dict[str, Any]:
        if len(self.points) != 1:
            raise ValueError(
                "Replay contains multiple evaluations. Use 'model_outputs_by_point'."
            )
        return dict(next(iter(self.points.values())).model_outputs)

    @property
    def absolute_errors(self) -> dict[str, float | None]:
        if len(self.points) != 1:
            raise ValueError(
                "Replay contains multiple evaluations. Inspect each point instead."
            )
        return dict(next(iter(self.points.values())).absolute_errors)

    @property
    def max_absolute_error(self) -> float | None:
        errors = [
            error
            for point in self.points.values()
            for error in point.absolute_errors.values()
            if error is not None
        ]
        return max(errors) if errors else None

    @property
    def is_consistent(self) -> bool:
        outputs_consistent = all(
            error is not None and error <= self.tolerance
            for point in self.points.values()
            for error in point.absolute_errors.values()
        )
        assertion_consistent = (
            self.expected_assertion_satisfied is None
            or self.assertion_satisfied == self.expected_assertion_satisfied
        )
        relation_consistent = self.relation_satisfied is not False
        return outputs_consistent and assertion_consistent and relation_consistent

    def to_records(self) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for name, point in self.points.items():
            record: dict[str, Any] = dict(point.inputs)
            if len(self.points) > 1:
                record["point"] = name
            for target, value in point.backend_outputs.items():
                record[f"forml_{target}"] = value
            for target, value in point.model_outputs.items():
                record[f"model_{target}"] = value
            for target, value in point.absolute_errors.items():
                record[f"absolute_error_{target}"] = value
            if len(self.points) > 1:
                record["relation_satisfied"] = self.relation_satisfied
                record["assertion_satisfied"] = self.assertion_satisfied
            record["is_consistent"] = self.is_consistent
            records.append(record)
        return records

    def to_record(self) -> dict[str, Any]:
        if len(self.points) != 1:
            raise ValueError("Replay contains multiple points. Use 'to_records'.")
        return self.to_records()[0]

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.to_records())

    def to_text(self) -> str:
        lines = [
            "FORML Counterexample Replay",
            f"Property      : {self.property_index + 1}",
            f"Consistent    : {'yes' if self.is_consistent else 'no'}",
            f"Tolerance     : {self.tolerance:g}",
        ]
        for name, point in self.points.items():
            lines.append(f"Point {name}")
            lines.extend(
                f"  {field} = {value}" for field, value in point.inputs.items()
            )
            for target in point.backend_outputs:
                lines.append(f"  {target} (FORML) = {point.backend_outputs[target]}")
                lines.append(f"  {target} (model) = {point.model_outputs.get(target)}")
                lines.append(f"  absolute error = {point.absolute_errors.get(target)}")
        lines.append(f"Relation      : {self.relation_satisfied}")
        lines.append(f"Assertion     : {self.assertion_satisfied}")
        return "\n".join(lines)

    def to_html(self) -> str:
        status = "consistent" if self.is_consistent else "mismatch"
        sections = "".join(_point_html(point) for point in self.points.values())
        return (
            '<div class="forml-replay" style="font-family:system-ui;'
            'border:1px solid #dbe3ee;border-radius:12px;padding:1rem">'
            f'<h3 style="margin-top:0">Counterexample replay · {status}</h3>'
            f"<p>Tolerance: <code>{self.tolerance:g}</code></p>"
            f"{sections}"
            f"<p>Relation: <code>{self.relation_satisfied}</code> · "
            f"Assertion: <code>{self.assertion_satisfied}</code></p></div>"
        )

    def _repr_html_(self) -> str:
        return self.to_html()


def replay_verification_report(
    report: VerificationReport,
    *,
    task: VerificationTaskIR2,
    schema: ModelSchema,
    model: object,
    tolerance: float = 1e-9,
) -> CounterexampleReplay:
    """Replay every distinct referenced evaluation against the real model."""

    predictor = getattr(model, "predict", None)
    if not callable(predictor):
        raise ReplayUnavailableError(
            "The supplied model does not expose a callable 'predict' method"
        )
    if not task.model_evaluations:
        raise ReplayUnavailableError("The property does not reference a model output")

    replay_points: dict[str, PointReplay] = {}
    concrete_outputs: dict[str, dict[str, Any]] = {}
    ordered_evaluations = _ordered_model_evaluations(task)
    for evaluation in ordered_evaluations:
        point_name = evaluation.point.name
        if point_name in replay_points:
            continue
        report_point = next(
            (item for item in report.points if item.name == point_name),
            None,
        )
        if report_point is None:
            raise ReplayUnavailableError(
                f"Required replay point {point_name!r} is missing from the report"
            )
        input_values = point_input_values(report_point)
        missing = [name for name in schema.features if name not in input_values]
        if missing:
            raise ReplayUnavailableError(
                f"Point {point_name!r} cannot be reconstructed; missing features: "
                + ", ".join(missing)
            )
        ordered_inputs = {name: input_values[name] for name in schema.features}
        prediction = _first_prediction(
            cast(_Predictor, model).predict(pd.DataFrame([ordered_inputs]))
        )
        model_outputs = {schema.target: python_report_value(prediction)}
        backend_outputs = point_output_values(report_point)
        if schema.target not in backend_outputs:
            raise ReplayUnavailableError(
                f"Point {point_name!r} has no formal output for {schema.target!r}"
            )
        errors = {
            schema.target: _absolute_error(
                backend_outputs[schema.target], model_outputs[schema.target]
            )
        }
        replay_points[point_name] = PointReplay(
            name=point_name,
            inputs=ordered_inputs,
            backend_outputs=backend_outputs,
            model_outputs=model_outputs,
            absolute_errors=errors,
        )
        concrete_outputs[point_name] = model_outputs

    point_inputs = {name: dict(point.inputs) for name, point in replay_points.items()}
    relation = (
        _evaluate_logical(
            task.scope.restriction.expression, point_inputs, concrete_outputs
        )
        if task.scope.restriction is not None
        else None
    )
    assertion = _evaluate_logical(
        task.spec_formula.expression,
        point_inputs,
        concrete_outputs,
    )
    expected = {
        VerificationStatus.COUNTEREXAMPLE: False,
        VerificationStatus.WITNESS: True,
    }.get(report.status)
    return CounterexampleReplay(
        property_index=report.property_index,
        points=replay_points,
        relation_satisfied=relation,
        assertion_satisfied=assertion,
        expected_assertion_satisfied=expected,
        tolerance=tolerance,
    )


def _ordered_model_evaluations(task: VerificationTaskIR2):
    """Return evaluations in canonical source-point order.

    Expression traversal order may reference ``x1`` before ``x0``. Public replay
    artifacts instead follow ``point_mappings``, which preserves declaration and
    binder order. Any manually injected evaluation without a point mapping is
    appended deterministically afterwards.
    """

    remaining = list(task.model_evaluations)
    ordered = []
    for mapping in task.point_mappings:
        matching = [
            evaluation
            for evaluation in remaining
            if evaluation.point == mapping.ir_point
        ]
        ordered.extend(matching)
        remaining = [
            evaluation for evaluation in remaining if evaluation not in matching
        ]
    ordered.extend(remaining)
    return tuple(ordered)


def _evaluate_logical(
    node: LogicalIR,
    inputs: Mapping[str, Mapping[str, Any]],
    outputs: Mapping[str, Mapping[str, Any]],
) -> bool:
    if isinstance(node, ComparisonIR):
        left = _evaluate_scalar(node.left, inputs, outputs)
        right = _evaluate_scalar(node.right, inputs, outputs)
        operator = node.op.value
        return {
            "==": left == right,
            "!=": left != right,
            "<": left < right,
            "<=": left <= right,
            ">": left > right,
            ">=": left >= right,
        }[operator]
    if isinstance(node, AndIR):
        return all(_evaluate_logical(item, inputs, outputs) for item in node.operands)
    if isinstance(node, OrIR):
        return any(_evaluate_logical(item, inputs, outputs) for item in node.operands)
    if isinstance(node, NotIR):
        return not _evaluate_logical(node.operand, inputs, outputs)
    if isinstance(node, ImplyIR):
        return (not _evaluate_logical(node.left, inputs, outputs)) or _evaluate_logical(
            node.right, inputs, outputs
        )
    raise ReplayUnavailableError(
        f"Replay cannot evaluate logical node {type(node).__name__}"
    )


def _evaluate_scalar(
    node: ScalarExpressionIR,
    inputs: Mapping[str, Mapping[str, Any]],
    outputs: Mapping[str, Mapping[str, Any]],
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
        try:
            return outputs[node.evaluation.point.name][node.evaluation.target_name]
        except KeyError as error:
            raise ReplayUnavailableError(
                "Replay output missing for "
                f"{node.evaluation.target_name}[{node.evaluation.point.name}]"
            ) from error
    if isinstance(node, UnaryArithmeticExpressionIR):
        value = _evaluate_scalar(node.operand, inputs, outputs)
        return -value if node.operator.value == "-" else +value
    if isinstance(node, BinaryArithmeticExpressionIR):
        left = _evaluate_scalar(node.left, inputs, outputs)
        right = _evaluate_scalar(node.right, inputs, outputs)
        return {
            "+": lambda: left + right,
            "-": lambda: left - right,
            "*": lambda: left * right,
            "/": lambda: left / right,
        }[node.operator.value]()
    raise ReplayUnavailableError(
        f"Replay cannot evaluate scalar node {type(node).__name__}"
    )


def _point_html(point: PointReplay) -> str:
    inputs = "".join(
        f"<li><code>{escape(name)}</code> = {escape(str(value))}</li>"
        for name, value in point.inputs.items()
    )
    rows = "".join(
        "<tr>"
        f"<td>{escape(name)}</td>"
        f"<td>{escape(str(point.backend_outputs[name]))}</td>"
        f"<td>{escape(str(point.model_outputs.get(name)))}</td>"
        f"<td>{escape(str(point.absolute_errors.get(name)))}</td>"
        "</tr>"
        for name in point.backend_outputs
    )
    return (
        f"<h4>Point {escape(point.name)}</h4><ul>{inputs}</ul>"
        '<table style="border-collapse:collapse;width:100%">'
        "<thead><tr><th>Output</th><th>FORML</th><th>Model</th>"
        f"<th>Absolute error</th></tr></thead><tbody>{rows}</tbody></table>"
    )


def _first_prediction(value: Any) -> Any:
    iloc = getattr(value, "iloc", None)
    if iloc is not None:
        return value.iloc[0]
    try:
        return value[0]
    except (IndexError, KeyError, TypeError):
        return value


def _absolute_error(left: Any, right: Any) -> float | None:
    try:
        return abs(float(left) - float(right))
    except (TypeError, ValueError):
        return 0.0 if left == right else None
