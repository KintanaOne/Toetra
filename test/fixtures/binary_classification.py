from __future__ import annotations

from dsl.semantic.types.enums import EnumDataType
from model.detector.model_framework import EnumModelFramework
from model.schema.feature_schema import FeatureSchema
from model.schema.model_schema import ModelSchema
from model.schema.output_schema import (
    BinaryClassificationDecisionPolicy,
    ClassificationOutputSchema,
)


def make_sklearn_logistic_schema(
    *,
    coefficient: float = 0.0,
    intercept: float = 0.0,
    labels: tuple[str, str] = ("rejected", "approved"),
) -> ModelSchema:
    """Build the normalized direct-binary LogisticRegression test schema."""

    negative_label, positive_label = labels
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LogisticRegression",
        features={
            "income": FeatureSchema(name="income", dtype=EnumDataType.FLOAT),
        },
        output_name="decision",
        task="classification",
        output_schema=ClassificationOutputSchema(
            label_dtype=EnumDataType.STRING,
            labels=labels,
            probability_available=True,
            decision_policy=BinaryClassificationDecisionPolicy(
                negative_label=negative_label,
                positive_label=positive_label,
            ),
        ),
        metadata={
            "linear": {
                "coef": [[coefficient]],
                "intercept": [intercept],
                "feature_names": ["income"],
            }
        },
    )


def binary_label_property(
    *,
    quantifier: str = "forall",
    label: str = "approved",
    backend: str | None = "Z3",
) -> str:
    backend_clause = f" using {backend}" if backend is not None else ""
    return f"""\
model := "credit.joblib"
target := decision

[LOGIC]:
{quantifier} applicant =>
    target[applicant].label == "{label}"{backend_clause}
"""


def binary_probability_property(
    *,
    quantifier: str = "forall",
    label: str = "approved",
    operator: str = ">=",
    threshold: str = "0.8",
    backend: str | None = "Z3",
) -> str:
    backend_clause = f" using {backend}" if backend is not None else ""
    return f"""\
model := "credit.joblib"
target := decision

[LOGIC]:
{quantifier} applicant =>
    target[applicant].probability("{label}") {operator} {threshold}{backend_clause}
"""
