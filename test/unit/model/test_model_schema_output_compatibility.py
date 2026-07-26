import pytest

from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.model_schema import ModelSchema
from toetra._models.schema.output_schema import (
    ClassificationOutputSchema,
    RegressionOutputSchema,
)


def test_output_name_and_schema_are_the_model_schema_source_of_truth() -> None:
    output = ClassificationOutputSchema(
        label_dtype=EnumDataType.STRING,
        labels=("rejected", "approved"),
        label_source_dtype="object",
        probability_available=True,
    )
    schema = ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="Classifier",
        features={},
        task="classification",
        output_name="decision",
        output_schema=output,
    )

    assert schema.output_name == "decision"
    assert schema.output is output
    assert schema.output_schema is output
    assert schema.target == "decision"
    assert schema.target_dtype is EnumDataType.STRING
    assert schema.target_source_dtype == "object"


def test_legacy_target_constructor_builds_regression_output_schema() -> None:
    schema = ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features={},
        target="score",
        task="regression",
        target_dtype=EnumDataType.FLOAT,
        target_source_dtype="float64",
    )

    assert schema.output_name == "score"
    assert schema.output_schema == RegressionOutputSchema(
        value_dtype=EnumDataType.FLOAT,
        value_source_dtype="float64",
    )


def test_legacy_classification_constructor_preserves_declared_classes() -> None:
    schema = ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="Classifier",
        features={},
        target="decision",
        task="classification",
        target_dtype=EnumDataType.INT,
        metadata={"classes": [0, 1]},
    )

    assert schema.output_schema == ClassificationOutputSchema(
        label_dtype=EnumDataType.INT,
        labels=(0, 1),
        probability_available=False,
    )


def test_model_schema_rejects_conflicting_output_names() -> None:
    with pytest.raises(ValueError, match="same output port"):
        ModelSchema(
            framework=EnumModelFramework.SKLEARN,
            model_type="LinearRegression",
            features={},
            target="score",
            output_name="decision",
            task="regression",
        )


def test_model_schema_rejects_conflicting_legacy_dtype_projection() -> None:
    with pytest.raises(ValueError, match="target_dtype"):
        ModelSchema(
            framework=EnumModelFramework.SKLEARN,
            model_type="LinearRegression",
            features={},
            target="score",
            task="regression",
            target_dtype=EnumDataType.INT,
            output_schema=RegressionOutputSchema(
                value_dtype=EnumDataType.FLOAT,
            ),
        )


def test_model_schema_rejects_task_and_output_kind_mismatch() -> None:
    with pytest.raises(ValueError, match="task conflicts"):
        ModelSchema(
            framework=EnumModelFramework.SKLEARN,
            model_type="Classifier",
            features={},
            output_name="decision",
            task="classification",
            output_schema=RegressionOutputSchema(),
        )
