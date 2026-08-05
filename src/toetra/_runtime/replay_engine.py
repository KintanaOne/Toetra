from __future__ import annotations

from typing import Any, Protocol

from toetra._backends.results import VerificationStatus
from toetra._compiler.ir.ir2.dsl.nodes import VerificationTaskIR2
from toetra._reporting.accessors import point_input_values, point_output_values
from toetra._reporting.evaluations import ReportModelEvaluation
from toetra._reporting.model import ReportPointEvidence
from toetra._runtime.errors import ReplayUnavailableError
from toetra._runtime.model_observer import ModelObservation, ModelObserverRegistry
from toetra._runtime.replay import CounterexampleReplay, EvaluationReplay, PointReplay
from toetra._runtime.replay_evaluation import absolute_error, evaluate_logical
from toetra._models.runtime.sklearn_observer import (
    create_default_model_observer_registry,
)
from toetra._models.schema.model_schema import ModelSchema


class ReplayReport(Protocol):
    """Read-only structural report contract required by concrete replay."""

    @property
    def property_index(self) -> int: ...

    @property
    def status(self) -> VerificationStatus: ...

    @property
    def points(self) -> tuple[ReportPointEvidence, ...]: ...

    @property
    def model_evaluations(self) -> tuple[ReportModelEvaluation, ...]: ...


def replay_verification_report(
    report: ReplayReport,
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
        evaluate_logical(
            task.scope.restriction.expression,
            point_inputs,
            concrete_observations,
            tolerance=tolerance,
        )
        if task.scope.restriction is not None
        else None
    )
    assertion_formula = task.source_spec_formula or task.spec_formula.expression
    assertion = evaluate_logical(
        assertion_formula,
        point_inputs,
        concrete_observations,
        tolerance=tolerance,
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
        label: absolute_error(value, concrete_probabilities.get(label))
        for label, value in formal_probabilities.items()
    }
    formal_quantities = {
        item.kind: item.python_value
        for item in formal.quantities
        if item.value is not None
    }
    concrete_quantities = dict(concrete.model_quantities)
    quantity_errors = {
        kind: absolute_error(value, concrete_quantities.get(kind))
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
                schema.output_name: absolute_error(
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
