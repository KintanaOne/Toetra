from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LinearRegression, LogisticRegression

from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.ir.affine import AffineModelIR
from toetra._models.ir_builder.sklearn_affine import SklearnAffineModelIRBuilder
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema


def _schema(
    model_type: str,
    feature_names: tuple[str, ...],
    *,
    task: str = "regression",
    framework: EnumModelFramework = EnumModelFramework.SKLEARN,
) -> ModelSchema:
    return ModelSchema(
        framework=framework,
        model_type=model_type,
        features=tuple(
            FeatureSchema(name=name, dtype=EnumDataType.FLOAT) for name in feature_names
        ),
        output_name="score",
        task=task,
    )


def test_builds_linear_regression_in_schema_order() -> None:
    inputs = pd.DataFrame({"income": [1.0, 2.0, 3.0], "debt": [3.0, 2.0, 1.0]})
    model = LinearRegression().fit(inputs, [2.0, 5.0, 8.0])

    result = SklearnAffineModelIRBuilder().build(
        model,
        _schema("LinearRegression", ("income", "debt")),
    )

    assert result == AffineModelIR(
        terms=(
            ("income", float(model.coef_[0])),
            ("debt", float(model.coef_[1])),
        ),
        bias=float(model.intercept_),
    )


def test_builds_binary_logistic_oriented_decision_affine_ir() -> None:
    inputs = pd.DataFrame(
        {"income": [1.0, 2.0, 3.0, 4.0], "debt": [4.0, 3.0, 2.0, 1.0]}
    )
    model = LogisticRegression(random_state=0).fit(inputs, [0, 0, 1, 1])

    result = SklearnAffineModelIRBuilder().build(
        model,
        _schema(
            "LogisticRegression",
            ("income", "debt"),
            task="classification",
        ),
    )

    assert result.terms == (
        ("income", float(model.coef_[0][0])),
        ("debt", float(model.coef_[0][1])),
    )
    assert result.bias == float(model.intercept_[0])


def test_rejects_unfitted_model() -> None:
    with pytest.raises(ValueError, match="not fitted"):
        SklearnAffineModelIRBuilder().build(
            LinearRegression(),
            _schema("LinearRegression", ("income",)),
        )


def test_rejects_unsupported_model_type() -> None:
    with pytest.raises(TypeError, match="requires an exact"):
        SklearnAffineModelIRBuilder().build(
            object(),
            _schema("LinearRegression", ("income",)),
        )


def test_rejects_schema_model_type_mismatch() -> None:
    model = LinearRegression().fit([[1.0], [2.0]], [2.0, 4.0])

    with pytest.raises(ValueError, match="model_type"):
        SklearnAffineModelIRBuilder().build(
            model,
            _schema("LogisticRegression", ("income",)),
        )


def test_rejects_schema_feature_order_mismatch() -> None:
    inputs = pd.DataFrame({"income": [1.0, 2.0, 3.0], "debt": [3.0, 2.0, 1.0]})
    model = LinearRegression().fit(inputs, [2.0, 5.0, 8.0])

    with pytest.raises(ValueError, match="feature order"):
        SklearnAffineModelIRBuilder().build(
            model,
            _schema("LinearRegression", ("debt", "income")),
        )


def test_rejects_schema_feature_count_mismatch() -> None:
    model = LinearRegression().fit([[1.0, 2.0], [2.0, 1.0]], [2.0, 4.0])

    with pytest.raises(ValueError, match="feature count"):
        SklearnAffineModelIRBuilder().build(
            model,
            _schema("LinearRegression", ("income",)),
        )


def test_rejects_multioutput_linear_regression() -> None:
    model = LinearRegression().fit(
        [[1.0, 2.0], [2.0, 1.0], [3.0, 0.0]],
        [[2.0, 3.0], [4.0, 2.0], [6.0, 1.0]],
    )

    with pytest.raises(ValueError, match="single-output"):
        SklearnAffineModelIRBuilder().build(
            model,
            _schema("LinearRegression", ("income", "debt")),
        )


def test_rejects_non_finite_parameters() -> None:
    model = LinearRegression().fit([[1.0], [2.0]], [2.0, 4.0])
    model.coef_ = np.asarray([np.inf])

    with pytest.raises(ValueError, match="finite"):
        SklearnAffineModelIRBuilder().build(
            model,
            _schema("LinearRegression", ("income",)),
        )
