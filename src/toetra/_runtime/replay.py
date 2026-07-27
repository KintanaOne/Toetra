from __future__ import annotations

import math
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

import pandas as pd

from toetra._runtime.replay_rendering import (
    evaluation_record,
    render_replay_html,
    render_replay_text,
)

__all__ = (
    "CounterexampleReplay",
    "EvaluationReplay",
    "PointReplay",
)


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

    def __post_init__(self) -> None:
        if not math.isfinite(self.tolerance) or self.tolerance < 0:
            raise ValueError("Replay tolerance must be a finite non-negative value")

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
    def assertion_consistent(self) -> bool:
        """Whether concrete assertion replay contradicts the formal result.

        ``None`` means that numeric replay landed inside the configured
        tolerance band around an ordering boundary. Such a result is
        indeterminate rather than contradictory.
        """

        return (
            self.expected_assertion_satisfied is None
            or self.assertion_satisfied is None
            or self.assertion_satisfied == self.expected_assertion_satisfied
        )

    @property
    def relation_consistent(self) -> bool:
        """Whether the concrete point is compatible with its scope restriction."""

        return self.relation_satisfied is not False

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
        return (
            outputs_consistent
            and evaluations_consistent
            and self.assertion_consistent
            and self.relation_consistent
        )

    def to_records(self) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for name, point in self.points.items():
            record: dict[str, Any] = dict(point.inputs)
            if len(self.points) > 1:
                record["point"] = name
            for target, value in point.backend_outputs.items():
                record[f"toetra_{target}"] = value
            for target, value in point.model_outputs.items():
                record[f"model_{target}"] = value
            for target, value in point.absolute_errors.items():
                record[f"absolute_error_{target}"] = value
            if point.evaluations:
                record["model_evaluations"] = tuple(
                    evaluation_record(item) for item in point.evaluations
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
        return render_replay_text(self)

    def to_html(self) -> str:
        return render_replay_html(self)

    def _repr_html_(self) -> str:
        return self.to_html()
