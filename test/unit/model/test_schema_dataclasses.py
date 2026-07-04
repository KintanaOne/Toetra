from dsl.semantic.types.enums import EnumDataType
from model.detector.model_framework import EnumModelFramework
from model.schema.feature_schema import FeatureSchema
from model.schema.model_schema import ModelSchema


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
    assert schema.target == "MyTarget"
    assert schema.features == features
    assert schema.metadata["model_class"] == "LogisticRegression"
