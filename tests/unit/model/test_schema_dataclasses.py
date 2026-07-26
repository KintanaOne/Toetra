from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema
from toetra._models.schema.output_schema import (
    ClassificationOutputSchema,
    RegressionOutputSchema,
)


def test_feature_schema_stores_name_dtype_and_nullable():
    schema = FeatureSchema(name="age", dtype=EnumDataType.INT, nullable=True)

    assert schema.name == "age"
    assert schema.dtype is EnumDataType.INT
    assert schema.nullable is True


def test_model_schema_stores_core_contract():
    features = {
        "age": FeatureSchema(name="age", dtype=EnumDataType.INT),
    }

    schema = ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LogisticRegression",
        features=features,
        target="MyTarget",
        task="classification",
        metadata={"model_class": "LogisticRegression"},
    )

    assert schema.framework is EnumModelFramework.SKLEARN
    assert schema.output_name == "MyTarget"
    assert schema.target == "MyTarget"
    assert schema.output_schema == ClassificationOutputSchema()
    assert schema.target_dtype is None
    assert schema.features == features
    assert schema.metadata["model_class"] == "LogisticRegression"


def test_model_schema_stores_optional_target_dtype():
    schema = ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features={},
        target="SalePrice",
        task="regression",
        target_dtype=EnumDataType.FLOAT,
    )

    assert schema.output_schema == RegressionOutputSchema(
        value_dtype=EnumDataType.FLOAT
    )
    assert schema.target_dtype is EnumDataType.FLOAT
