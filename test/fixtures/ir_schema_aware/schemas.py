from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema
from toetra._models.schema.output_schema import ClassificationOutputSchema


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


def make_binary_classification_schema() -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LogisticRegression",
        task="classification",
        output_name="decision",
        output_schema=ClassificationOutputSchema(
            label_dtype=EnumDataType.STRING,
            labels=("rejected", "approved"),
            probability_available=True,
        ),
        features={
            "income": FeatureSchema(
                name="income", dtype=EnumDataType.FLOAT, nullable=False
            )
        },
        metadata={},
    )
