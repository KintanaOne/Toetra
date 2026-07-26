from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import pandas as pd
import pytest
from sklearn.linear_model import LinearRegression, LogisticRegression

from toetra._runtime.errors import ReplayUnavailableError
from toetra._runtime.model_observer import (
    ModelObservation,
    ModelObserverRegistry,
)
from toetra._models.introspector.sklearn_introspector import SklearnIntrospector
from toetra._models.runtime.sklearn_observer import SklearnModelObserver


def _classification_artifacts(tmp_path):
    frame = pd.DataFrame(
        {
            "income": [-3.0, -2.0, -1.0, 1.0, 2.0, 3.0],
            "decision": [0, 0, 0, 1, 1, 1],
        }
    )
    model = LogisticRegression(random_state=0, max_iter=1000).fit(
        frame[["income"]], frame["decision"]
    )
    dataset = tmp_path / "classification.csv"
    frame.to_csv(dataset, index=False)
    schema = SklearnIntrospector(
        model=model,
        source_path=dataset,
        target_name="decision",
    ).introspect()
    return model, schema


def _regression_artifacts(tmp_path):
    frame = pd.DataFrame(
        {
            "a": [0.0, 1.0, 2.0],
            "score": [1.0, 3.0, 5.0],
        }
    )
    model = LinearRegression().fit(frame[["a"]], frame["score"])
    dataset = tmp_path / "regression.csv"
    frame.to_csv(dataset, index=False)
    schema = SklearnIntrospector(
        model=model,
        source_path=dataset,
        target_name="score",
    ).introspect()
    return model, schema


def test_sklearn_observer_normalizes_binary_classification_views(tmp_path) -> None:
    model, schema = _classification_artifacts(tmp_path)

    observation = SklearnModelObserver().observe(
        schema=schema,
        model=model,
        inputs={"income": 2.0},
    )

    assert observation.output_name == "decision"
    assert observation.predicted_label == 1
    assert set(observation.class_probabilities) == {0, 1}
    assert sum(observation.class_probabilities.values()) == pytest.approx(1.0)
    assert "oriented_decision_value" in observation.model_quantities
    assert observation.model_quantities["oriented_decision_value"] > 0


def test_sklearn_observer_preserves_regression_replay_contract(tmp_path) -> None:
    model, schema = _regression_artifacts(tmp_path)

    observation = SklearnModelObserver().observe(
        schema=schema,
        model=model,
        inputs={"a": 2.0},
    )

    assert observation.output_name == "score"
    assert observation.regression_value == pytest.approx(5.0)
    assert observation.class_probabilities == {}
    assert observation.model_quantities == {}


def test_sklearn_observer_rejects_missing_features(tmp_path) -> None:
    model, schema = _classification_artifacts(tmp_path)

    with pytest.raises(ReplayUnavailableError, match="missing model features"):
        SklearnModelObserver().observe(schema=schema, model=model, inputs={})


@dataclass
class _CustomObserver:
    observer_id: str = "custom-observer"

    def supports(self, *, schema, model: object) -> bool:
        return model is _CUSTOM_MODEL

    def observe(
        self,
        *,
        schema,
        model: object,
        inputs: Mapping[str, Any],
    ) -> ModelObservation:
        return ModelObservation(output_name=schema.output_name, regression_value=1.0)


_CUSTOM_MODEL = object()


def test_observer_registry_selects_protocol_implementation_without_type_checks(
    tmp_path,
) -> None:
    _model, schema = _regression_artifacts(tmp_path)
    registry = ModelObserverRegistry((_CustomObserver(),))

    selected = registry.require(schema=schema, model=_CUSTOM_MODEL)

    assert selected.observer_id == "custom-observer"


def test_observer_registry_rejects_unsupported_runtime_model(tmp_path) -> None:
    _model, schema = _regression_artifacts(tmp_path)

    with pytest.raises(ReplayUnavailableError, match="No model runtime observer"):
        ModelObserverRegistry().require(schema=schema, model=object())
