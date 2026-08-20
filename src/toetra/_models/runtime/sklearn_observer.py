from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, cast

import pandas as pd

from toetra._reporting.values import python_report_value
from toetra._runtime.errors import ReplayUnavailableError
from toetra._runtime.model_observer import ModelObservation, ModelObserverRegistry
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.model_schema import ModelSchema
from toetra._models.schema.output_schema import (
    ClassificationOutputSchema,
    RegressionOutputSchema,
)


class SklearnModelObserver:
    """Concrete observer for normalized sklearn regression/classification models."""

    observer_id = "sklearn-runtime-observer-v1"

    def supports(self, *, schema: ModelSchema, model: object) -> bool:
        return schema.framework is EnumModelFramework.SKLEARN and callable(
            getattr(model, "predict", None)
        )

    def observe(
        self,
        *,
        schema: ModelSchema,
        model: object,
        inputs: Mapping[str, Any],
    ) -> ModelObservation:
        missing = tuple(name for name in schema.feature_names if name not in inputs)
        if missing:
            raise ReplayUnavailableError(
                "Concrete observation is missing model features: " + ", ".join(missing)
            )

        frame = pd.DataFrame([{name: inputs[name] for name in schema.feature_names}])
        output_schema = schema.output_schema
        runtime_model = cast(Any, model)

        if isinstance(output_schema, RegressionOutputSchema):
            prediction = _first_value(runtime_model.predict(frame))
            return ModelObservation(
                output_name=schema.output_name,
                regression_value=python_report_value(prediction),
            )

        if isinstance(output_schema, ClassificationOutputSchema):
            predict = getattr(runtime_model, "predict", None)
            predict_proba = getattr(runtime_model, "predict_proba", None)
            decision_function = getattr(runtime_model, "decision_function", None)
            if not callable(predict) or not callable(predict_proba):
                raise ReplayUnavailableError(
                    "Classification replay requires callable predict and predict_proba"
                )
            if output_schema.decision_policy is not None and not callable(
                decision_function
            ):
                raise ReplayUnavailableError(
                    "The binary logistic profile requires decision_function for replay"
                )

            predicted_label = python_report_value(_first_value(predict(frame)))
            probabilities = _first_row(predict_proba(frame))
            if len(probabilities) != len(output_schema.labels):
                raise ReplayUnavailableError(
                    "predict_proba output width does not match the normalized labels"
                )
            class_probabilities = {
                label: float(probability)
                for label, probability in zip(
                    output_schema.labels,
                    probabilities,
                    strict=True,
                )
            }
            quantities: dict[str, float] = {}
            if callable(decision_function):
                quantities["oriented_decision_value"] = float(
                    python_report_value(_first_value(decision_function(frame)))
                )
            return ModelObservation(
                output_name=schema.output_name,
                predicted_label=predicted_label,
                class_probabilities=class_probabilities,
                model_quantities=quantities,
            )

        raise ReplayUnavailableError(
            f"Unsupported output schema for replay: {type(output_schema).__name__}"
        )


def create_default_model_observer_registry() -> ModelObserverRegistry:
    registry = ModelObserverRegistry()
    registry.register(SklearnModelObserver())
    return registry


def _first_value(value: Any) -> Any:
    iloc = getattr(value, "iloc", None)
    if iloc is not None:
        return value.iloc[0]
    try:
        return value[0]
    except (IndexError, KeyError, TypeError):
        return value


def _first_row(value: Any) -> list[Any]:
    iloc = getattr(value, "iloc", None)
    if iloc is not None:
        row = value.iloc[0]
    else:
        try:
            row = value[0]
        except (IndexError, KeyError, TypeError) as error:
            raise ReplayUnavailableError(
                "predict_proba did not return a row-like result"
            ) from error
    tolist = getattr(row, "tolist", None)
    if callable(tolist):
        row = tolist()
    try:
        return list(cast(Iterable[Any], row))
    except TypeError as error:
        raise ReplayUnavailableError(
            "predict_proba did not return an iterable probability row"
        ) from error
