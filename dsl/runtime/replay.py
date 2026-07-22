from __future__ import annotations

from dataclasses import dataclass, field
from html import escape
from types import MappingProxyType
from typing import Any, Mapping

import pandas as pd

from dsl.backends.results import VerificationStatus
from dsl.ir.ir1.model_quantities import ModelQuantityExpressionIR
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
from dsl.ir.ir1.outputs import OutputObservableExpressionIR
from dsl.ir.ir2.nodes import VerificationTaskIR2
from dsl.reporting.accessors import point_input_values, point_output_values
from dsl.reporting.evaluations import ReportModelEvaluation
from dsl.reporting.model import VerificationReport
from dsl.runtime.errors import ReplayUnavailableError
from dsl.runtime.model_observer import (
    ModelObservation,
    ModelObserverRegistry,
)
from model.runtime.sklearn_observer import create_default_model_observer_registry
from model.schema.model_schema import ModelSchema
from model.schema.output_schema import EnumOutputObservable


@dataclass(frozen=True)
class EvaluationReplay:
    """Concrete comparison of every relevant view of one model evaluation."""

    output_name: str
    formal_label: Any | None = None
    model_label: Any | None = None
    label_matches: bool | None = None
    formal_probabilities: Mapping[Any, float] = field(
        default_factory=lambda: MappingProxyType({})
    )
    model_probabilities: Mapping[Any, float] = field(
        default_factory=lambda: MappingProxyType({})
    )
    probability_errors: Mapping[Any, float | None] = field(
        default_factory=lambda: MappingProxyType({})
    )
    formal_quantities: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )
    model_quantities: Mapping[str, float] = field(
        default_factory=lambda: MappingProxyType({})
    )
    quantity_errors: Mapping[str, float | None] = field(
        default_factory=lambda: MappingProxyType({})
    )

    def __post_init__(self) -> None:
        for name in (
            "formal_probabilities",
            "model_probabilities",
            "probability_errors",
            "formal_quantities",
            "model_quantities",
            "quantity_errors",
        ):
            object.__setattr__(self, name, MappingProxyType(dict(getattr(self, name))))

    def is_consistent(self, *, tolerance: float) -> bool:
        label_consistent = self.label_matches is not False
        probability_consistent = all(
            error is not None and error <= tolerance
            for error in self.probability_errors.values()
        )
        quantity_consistent = all(
            error is not None and error <= tolerance
            for error in self.quantity_errors.values()
        )
        return label_consistent and probability_consistent and quantity_consistent


@dataclass(frozen=True)
class PointReplay:
    """Concrete replay evidence for one distinct model-input point."""

    name: str
    inputs: Mapping[str, Any]
    backend_outputs: Mapping[str, Any]
    model_outputs: Mapping[str, Any]
    absolute_errors: Mapping[str, float | None]
    evaluations: tuple[EvaluationReplay, ...] = ()

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
        errors.extend(
            error
            for point in self.points.values()
            for evaluation in point.evaluations
            for error in (
                *evaluation.probability_errors.values(),
                *evaluation.quantity_errors.values(),
            )
            if error is not None
        )
        return max(errors) if errors else None

    @property
    def is_consistent(self) -> bool:
        outputs_consistent = all(
            error is not None and error <= self.tolerance
            for point in self.points.values()
            for error in point.absolute_errors.values()
        )
        evaluations_consistent = all(
            evaluation.is_consistent(tolerance=self.tolerance)
            for point in self.points.values()
            for evaluation in point.evaluations
        )
        assertion_consistent = (
            self.expected_assertion_satisfied is None
            or self.assertion_satisfied == self.expected_assertion_satisfied
        )
        relation_consistent = self.relation_satisfied is not False
        return (
            outputs_consistent
            and evaluations_consistent
            and assertion_consistent
            and relation_consistent
        )

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
            if point.evaluations:
                record["model_evaluations"] = tuple(
                    _evaluation_record(item) for item in point.evaluations
                )
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
            for evaluation in point.evaluations:
                lines.append(f"  Evaluation {evaluation.output_name}")
                if evaluation.formal_label is not None:
                    lines.append(
                        f"    label: FORML={evaluation.formal_label}, "
                        f"model={evaluation.model_label}, "
                        f"match={evaluation.label_matches}"
                    )
                for label, formal in evaluation.formal_probabilities.items():
                    lines.append(
                        f"    probability({label!r}): FORML={formal}, "
                        f"model={evaluation.model_probabilities.get(label)}, "
                        f"error={evaluation.probability_errors.get(label)}"
                    )
                for quantity, formal in evaluation.formal_quantities.items():
                    lines.append(
                        f"    {quantity}: FORML={formal}, "
                        f"model={evaluation.model_quantities.get(quantity)}, "
                        f"error={evaluation.quantity_errors.get(quantity)}"
                    )
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
    observer_registry: ModelObserverRegistry | None = None,
) -> CounterexampleReplay:
    """Replay every distinct referenced evaluation against the real model."""

    if not task.model_evaluations:
        raise ReplayUnavailableError("The property does not reference a model output")

    registry = observer_registry or create_default_model_observer_registry()
    observer = registry.require(schema=schema, model=model)
    replay_points: dict[str, PointReplay] = {}
    concrete_observations: dict[str, ModelObservation] = {}
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
        observation = observer.observe(
            schema=schema,
            model=model,
            inputs=ordered_inputs,
        )
        concrete_observations[point_name] = observation

        report_evaluations = tuple(
            item
            for item in report.model_evaluations
            if item.point_name == point_name
            and item.output_name == evaluation.output_name
        )
        evaluation_replays = tuple(
            _compare_classification_evaluation(item, observation)
            for item in report_evaluations
        )
        backend_outputs, model_outputs, errors = _legacy_output_comparison(
            report_point=report_point,
            schema=schema,
            observation=observation,
            evaluation_replays=evaluation_replays,
        )
        replay_points[point_name] = PointReplay(
            name=point_name,
            inputs=ordered_inputs,
            backend_outputs=backend_outputs,
            model_outputs=model_outputs,
            absolute_errors=errors,
            evaluations=evaluation_replays,
        )

    point_inputs = {name: dict(point.inputs) for name, point in replay_points.items()}
    relation = (
        _evaluate_logical(
            task.scope.restriction.expression,
            point_inputs,
            concrete_observations,
        )
        if task.scope.restriction is not None
        else None
    )
    assertion_formula = task.source_spec_formula or task.spec_formula.expression
    assertion = _evaluate_logical(
        assertion_formula,
        point_inputs,
        concrete_observations,
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


def _compare_classification_evaluation(
    formal: ReportModelEvaluation,
    concrete: ModelObservation,
) -> EvaluationReplay:
    formal_probabilities = {
        item.label: float(item.value)
        for item in formal.probabilities
        if item.value is not None
    }
    concrete_probabilities = dict(concrete.class_probabilities)
    probability_errors = {
        label: _absolute_error(value, concrete_probabilities.get(label))
        for label, value in formal_probabilities.items()
    }
    formal_quantities = {
        item.kind: item.python_value
        for item in formal.quantities
        if item.value is not None
    }
    concrete_quantities = dict(concrete.model_quantities)
    quantity_errors = {
        kind: _absolute_error(value, concrete_quantities.get(kind))
        for kind, value in formal_quantities.items()
    }
    label_matches = (
        None
        if formal.predicted_label is None or concrete.predicted_label is None
        else formal.predicted_label == concrete.predicted_label
    )
    return EvaluationReplay(
        output_name=formal.output_name,
        formal_label=formal.predicted_label,
        model_label=concrete.predicted_label,
        label_matches=label_matches,
        formal_probabilities=formal_probabilities,
        model_probabilities=concrete_probabilities,
        probability_errors=probability_errors,
        formal_quantities=formal_quantities,
        model_quantities=concrete_quantities,
        quantity_errors=quantity_errors,
    )


def _legacy_output_comparison(
    *,
    report_point: object,
    schema: ModelSchema,
    observation: ModelObservation,
    evaluation_replays: tuple[EvaluationReplay, ...],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, float | None]]:
    backend_outputs = point_output_values(report_point)
    if backend_outputs:
        if observation.regression_value is None:
            raise ReplayUnavailableError(
                f"Concrete observer returned no regression value for {schema.output_name!r}"
            )
        model_outputs = {schema.output_name: observation.regression_value}
        if schema.output_name not in backend_outputs:
            raise ReplayUnavailableError(
                f"Point has no formal output for {schema.output_name!r}"
            )
        return (
            backend_outputs,
            model_outputs,
            {
                schema.output_name: _absolute_error(
                    backend_outputs[schema.output_name],
                    model_outputs[schema.output_name],
                )
            },
        )

    formal_flat: dict[str, Any] = {}
    concrete_flat: dict[str, Any] = {}
    errors: dict[str, float | None] = {}
    for evaluation in evaluation_replays:
        if evaluation.formal_label is not None:
            key = f"{evaluation.output_name}.label"
            formal_flat[key] = evaluation.formal_label
            concrete_flat[key] = evaluation.model_label
            errors[key] = 0.0 if evaluation.label_matches else None
        for label, formal in evaluation.formal_probabilities.items():
            key = f"{evaluation.output_name}.probability[{label!r}]"
            formal_flat[key] = formal
            concrete_flat[key] = evaluation.model_probabilities.get(label)
            errors[key] = evaluation.probability_errors.get(label)
    return formal_flat, concrete_flat, errors


def _ordered_model_evaluations(task: VerificationTaskIR2):
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
    observations: Mapping[str, ModelObservation],
) -> bool:
    if isinstance(node, ComparisonIR):
        left = _evaluate_scalar(node.left, inputs, observations)
        right = _evaluate_scalar(node.right, inputs, observations)
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
        return all(
            _evaluate_logical(item, inputs, observations) for item in node.operands
        )
    if isinstance(node, OrIR):
        return any(
            _evaluate_logical(item, inputs, observations) for item in node.operands
        )
    if isinstance(node, NotIR):
        return not _evaluate_logical(node.operand, inputs, observations)
    if isinstance(node, ImplyIR):
        return (
            not _evaluate_logical(node.left, inputs, observations)
        ) or _evaluate_logical(node.right, inputs, observations)
    raise ReplayUnavailableError(
        f"Replay cannot evaluate logical node {type(node).__name__}"
    )


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
    evaluation_html = "".join(_evaluation_html(item) for item in point.evaluations)
    return (
        f"<h4>Point {escape(point.name)}</h4><ul>{inputs}</ul>"
        '<table style="border-collapse:collapse;width:100%">'
        "<thead><tr><th>Output</th><th>FORML</th><th>Model</th>"
        f"<th>Absolute error</th></tr></thead><tbody>{rows}</tbody></table>"
        f"{evaluation_html}"
    )


def _evaluation_html(evaluation: EvaluationReplay) -> str:
    rows: list[str] = []
    if evaluation.formal_label is not None:
        rows.append(
            "<tr><td>label</td>"
            f"<td>{escape(str(evaluation.formal_label))}</td>"
            f"<td>{escape(str(evaluation.model_label))}</td>"
            f"<td>{escape(str(evaluation.label_matches))}</td></tr>"
        )
    for label, formal in evaluation.formal_probabilities.items():
        rows.append(
            f"<tr><td>probability({escape(str(label))})</td>"
            f"<td>{escape(str(formal))}</td>"
            f"<td>{escape(str(evaluation.model_probabilities.get(label)))}</td>"
            f"<td>{escape(str(evaluation.probability_errors.get(label)))}</td></tr>"
        )
    for kind, formal in evaluation.formal_quantities.items():
        rows.append(
            f"<tr><td>{escape(kind)}</td>"
            f"<td>{escape(str(formal))}</td>"
            f"<td>{escape(str(evaluation.model_quantities.get(kind)))}</td>"
            f"<td>{escape(str(evaluation.quantity_errors.get(kind)))}</td></tr>"
        )
    return (
        f"<h5>Evaluation {escape(evaluation.output_name)}</h5>"
        '<table style="border-collapse:collapse;width:100%">'
        "<thead><tr><th>View</th><th>FORML</th><th>Model</th><th>Match/error</th>"
        f"</tr></thead><tbody>{''.join(rows)}</tbody></table>"
    )


def _evaluation_record(evaluation: EvaluationReplay) -> dict[str, Any]:
    return {
        "output_name": evaluation.output_name,
        "formal_label": evaluation.formal_label,
        "model_label": evaluation.model_label,
        "label_matches": evaluation.label_matches,
        "formal_probabilities": dict(evaluation.formal_probabilities),
        "model_probabilities": dict(evaluation.model_probabilities),
        "probability_errors": dict(evaluation.probability_errors),
        "formal_quantities": dict(evaluation.formal_quantities),
        "model_quantities": dict(evaluation.model_quantities),
        "quantity_errors": dict(evaluation.quantity_errors),
    }


def _absolute_error(left: Any, right: Any) -> float | None:
    if right is None:
        return None
    try:
        return abs(float(left) - float(right))
    except (TypeError, ValueError):
        return 0.0 if left == right else None
