from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LinearRegression

from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.errors.introspection import MissingFeatureMetadataError
from toetra._models.introspector.sklearn_introspector import SklearnIntrospector


def test_model_feature_names_exclude_lookup_metadata_columns(tmp_path) -> None:
    data = pd.DataFrame(
        {
            "application_id": ["A-1", "A-2", "A-3"],
            "income": [30_000.0, 45_000.0, 60_000.0],
            "debt_ratio": [0.6, 0.4, 0.2],
            "score": [0.8, 0.5, 0.2],
        }
    )
    dataset = tmp_path / "applications.csv"
    data.to_csv(dataset, index=False)
    model = LinearRegression().fit(
        data[["income", "debt_ratio"]],
        data["score"],
    )

    schema = SklearnIntrospector(
        model=model,
        source_path=dataset,
        target_name="score",
    ).introspect()

    assert tuple(schema.features) == ("income", "debt_ratio")
    assert "application_id" not in schema.features
    assert schema.features["income"].dtype is EnumDataType.FLOAT


def test_model_feature_order_wins_over_dataset_column_order(tmp_path) -> None:
    training = pd.DataFrame(
        {
            "income": [30_000.0, 45_000.0, 60_000.0],
            "debt_ratio": [0.6, 0.4, 0.2],
        }
    )
    model = LinearRegression().fit(training, [0.8, 0.5, 0.2])
    dataset = tmp_path / "reordered.csv"
    pd.DataFrame(
        {
            "debt_ratio": training["debt_ratio"],
            "lookup_id": ["A-1", "A-2", "A-3"],
            "income": training["income"],
            "score": [0.8, 0.5, 0.2],
        }
    ).to_csv(dataset, index=False)

    schema = SklearnIntrospector(
        model=model,
        source_path=dataset,
        target_name="score",
    ).introspect()

    assert tuple(schema.features) == ("income", "debt_ratio")


def test_missing_model_declared_feature_is_rejected(tmp_path) -> None:
    training = pd.DataFrame(
        {
            "income": [30_000.0, 45_000.0, 60_000.0],
            "debt_ratio": [0.6, 0.4, 0.2],
        }
    )
    model = LinearRegression().fit(training, [0.8, 0.5, 0.2])
    dataset = tmp_path / "missing_feature.csv"
    pd.DataFrame(
        {
            "income": training["income"],
            "score": [0.8, 0.5, 0.2],
        }
    ).to_csv(dataset, index=False)

    with pytest.raises(MissingFeatureMetadataError, match="debt_ratio"):
        SklearnIntrospector(
            model=model,
            source_path=dataset,
            target_name="score",
        ).introspect()


def test_unnamed_model_keeps_non_target_dataset_fallback(tmp_path) -> None:
    inputs = np.asarray([[1.0], [2.0], [3.0]])
    model = LinearRegression().fit(inputs, [3.0, 5.0, 7.0])
    dataset = tmp_path / "unnamed.csv"
    pd.DataFrame(
        {
            "a": [1.0, 2.0, 3.0],
            "score": [3.0, 5.0, 7.0],
        }
    ).to_csv(dataset, index=False)

    schema = SklearnIntrospector(
        model=model,
        source_path=dataset,
        target_name="score",
    ).introspect()

    assert tuple(schema.features) == ("a",)
