import pandas as pd
import pytest
from sklearn.linear_model import LinearRegression

from dsl.semantic.types.enums import EnumDataType
from model.detector.model_framework import EnumModelFramework
from model.errors.introspection import MissingFeatureMetadataError
from model.introspector.sklearn_introspector import SklearnIntrospector
from model.schema.feature_schema import FeatureSchema
from model.schema.model_schema import ModelSchema
from test.fixtures.model_bridge.factories import (
    dataset_path,
    train_classification_model,
)


def test_sklearn_introspector_builds_classification_schema_with_explicit_target():
    model = train_classification_model()

    schema = SklearnIntrospector(
        model=model,
        source_path=dataset_path("classification.csv"),
        target_name="MyTarget",
        serialization_format=".joblib",
    ).introspect()

    assert schema.framework is EnumModelFramework.SKLEARN
    assert schema.model_type == "LogisticRegression"
    assert schema.task == "classification"
    assert schema.target == "MyTarget"
    assert schema.target_dtype is EnumDataType.INT
    assert "MyTarget" not in schema.features
    assert set(schema.features) == {"age", "income", "score"}
    assert schema.features["age"].dtype is EnumDataType.INT
    assert schema.features["score"].dtype is EnumDataType.FLOAT
    assert schema.metadata["serialization_format"] == ".joblib"
    assert schema.metadata["model_class"] == "LogisticRegression"
    assert schema.metadata["n_features_in"] == 3


def test_sklearn_introspector_preserves_integer_target_dtype_for_regression(
    tmp_path,
):
    data = pd.DataFrame(
        {
            "feature": [1.0, 2.0, 3.0],
            "SalePrice": [100, 200, 300],
        }
    )
    dataset = tmp_path / "integer_regression_target.csv"
    data.to_csv(dataset, index=False)

    model = LinearRegression()
    model.fit(data[["feature"]], data["SalePrice"])

    schema = SklearnIntrospector(
        model=model,
        source_path=dataset,
        target_name="SalePrice",
    ).introspect()

    assert schema.task == "regression"
    assert schema.target_dtype is EnumDataType.INT


def test_sklearn_introspector_detects_nullable_columns():
    model = train_classification_model()

    schema = SklearnIntrospector(
        model=model,
        source_path=dataset_path("nullable.csv"),
        target_name="MyTarget",
    ).introspect()

    assert schema.features["income"].nullable is True
    assert schema.features["score"].nullable is True
    assert schema.features["age"].nullable is False


def test_sklearn_introspector_uses_external_schema_before_target_name():
    model = train_classification_model()
    external_schema = ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="ExternalSchema",
        features={
            "external_feature": FeatureSchema(
                name="external_feature",
                dtype=EnumDataType.FLOAT,
            )
        },
        target="ExternalTarget",
        task="classification",
        target_dtype=EnumDataType.STRING,
    )

    schema = SklearnIntrospector(
        model=model,
        schema=external_schema,
        target_name="MyTarget",
    ).introspect()

    assert schema.target == "ExternalTarget"
    assert schema.target_dtype is EnumDataType.STRING
    assert set(schema.features) == {"external_feature"}


def test_sklearn_introspector_raises_when_no_dataset_or_schema_is_available():
    model = train_classification_model()

    with pytest.raises(MissingFeatureMetadataError):
        SklearnIntrospector(
            model=model,
            source_path=None,
            schema=None,
            target_name="MyTarget",
        ).introspect()
