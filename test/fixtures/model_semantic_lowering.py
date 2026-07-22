from __future__ import annotations

from dsl.compatibility.descriptors import (
    FrameworkModelDescriptor,
    NumericSemanticDescriptor,
)
from dsl.semantic.types.enums import EnumDataType
from model.detector.model_framework import EnumModelFramework
from model.schema.feature_schema import FeatureSchema
from model.schema.model_schema import ModelSchema
from model.schema.output_schema import ClassificationOutputSchema
from model.semantics.binary_classification import (
    BINARY_LOGISTIC_AFFINE_MODEL_FAMILY,
)


def make_binary_logistic_schema(
    *,
    labels: tuple[str, str] = ("rejected", "approved"),
    model_family: str = BINARY_LOGISTIC_AFFINE_MODEL_FAMILY,
) -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="SemanticFixtureClassifier",
        task="classification",
        output_name="decision",
        output_schema=ClassificationOutputSchema(
            label_dtype=EnumDataType.STRING,
            labels=labels,
            probability_available=True,
        ),
        features={
            "income": FeatureSchema(
                name="income",
                dtype=EnumDataType.FLOAT,
                nullable=False,
            )
        },
        compatibility=FrameworkModelDescriptor(
            framework_adapter_id="semantic_fixture",
            model_family=model_family,
            source_execution_profile_id="exact_real_fixture",
            numeric_semantics=NumericSemanticDescriptor.exact_real(),
            output_dtype="string",
        ),
    )


def label_property(
    *,
    operator: str = "==",
    label: str = "approved",
    observable_on_left: bool = True,
) -> str:
    left = "target[applicant].label"
    right = f'"{label}"'
    comparison = (
        f"{left} {operator} {right}"
        if observable_on_left
        else f"{right} {operator} {left}"
    )
    return f"""\
model := "credit.joblib"
target := decision

[LOGIC]:
forall applicant =>
    {comparison}
"""
