import pandas as pd
import pytest
from sklearn.linear_model import LinearRegression

from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.errors.introspection import MissingFeatureMetadataError
from toetra._models.introspector.sklearn_introspector import SklearnIntrospector
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema
from toetra._models.schema.output_schema import (
    BinaryClassificationDecisionPolicy,
    ClassificationOutputSchema,
    EnumOutputObservable,
    RegressionOutputSchema,
)
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
    assert schema.output_name == "MyTarget"
    assert schema.target == "MyTarget"
    assert schema.output_schema == ClassificationOutputSchema(
        label_dtype=EnumDataType.INT,
        labels=(0, 1),
        label_source_dtype="int64",
        probability_available=True,
        decision_policy=BinaryClassificationDecisionPolicy(
            negative_label=0,
            positive_label=1,
        ),
    )
    assert schema.output_schema.available_observables == (
        EnumOutputObservable.PREDICTED_LABEL,
        EnumOutputObservable.CLASS_PROBABILITY,
    )
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
    assert schema.output_schema == RegressionOutputSchema(
        value_dtype=EnumDataType.INT,
        value_source_dtype="int64",
    )
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

    assert schema.output_name == "ExternalTarget"
    assert schema.target == "ExternalTarget"
    assert schema.output_schema == ClassificationOutputSchema(
        label_dtype=EnumDataType.STRING,
        labels=(0, 1),
        probability_available=True,
        decision_policy=BinaryClassificationDecisionPolicy(
            negative_label=0,
            positive_label=1,
        ),
    )
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
