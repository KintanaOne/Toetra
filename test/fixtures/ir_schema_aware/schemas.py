from dsl.semantic.types.enums import EnumDataType
from model.detector.model_framework import EnumModelFramework
from model.schema.feature_schema import FeatureSchema
from model.schema.model_schema import ModelSchema


def make_schema() -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LogisticRegression",
        task="classification",
        target="MyTarget",
        features={
            "age": FeatureSchema(
                name="age",
                dtype=EnumDataType.INT,
                nullable=False,
            ),
            "income": FeatureSchema(
                name="income",
                dtype=EnumDataType.FLOAT,
                nullable=False,
            ),
            "is_active": FeatureSchema(
                name="is_active",
                dtype=EnumDataType.BOOL,
                nullable=False,
            ),
        },
        metadata={},
    )
