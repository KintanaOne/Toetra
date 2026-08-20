from __future__ import annotations

import math
from dataclasses import replace

import pytest

from toetra._compiler.ir.ir1.model_quantities import EnumModelQuantityKind
from toetra._compiler.ir.ir1.nodes import ModelEvaluationIR, PointBindingIR
from toetra._compiler.ir.ir2.model.affine import AffineModelQuantityConstraintIR2
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.encoder.errors import (
    MissingModelParameterError,
    UnsupportedModelEncoderError,
    UnsupportedModelParameterError,
)
from toetra._models.encoder.factory import ModelEncoderFactory
from toetra._models.encoder.sklearn.logistic import SklearnLogisticRegressionEncoder
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema
from toetra._models.schema.output_schema import (
    BinaryClassificationDecisionPolicy,
    ClassificationOutputSchema,
)
from toetra._compiler.semantic.types.enums import EnumDataType


def _schema(*, coefficient: float = 1.5) -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LogisticRegression",
        features={
            "income": FeatureSchema(name="income", dtype=EnumDataType.FLOAT),
            "debt": FeatureSchema(name="debt", dtype=EnumDataType.FLOAT),
        },
        output_name="decision",
        task="classification",
        output_schema=ClassificationOutputSchema(
            label_dtype=EnumDataType.STRING,
            labels=("rejected", "approved"),
            probability_available=True,
            decision_policy=BinaryClassificationDecisionPolicy(
                negative_label="rejected",
                positive_label="approved",
            ),
        ),
        metadata={
            "linear": {
                "coef": [[coefficient, -2.0]],
                "intercept": [0.25],
                "feature_names": ["income", "debt"],
            }
        },
    )


def _evaluation() -> ModelEvaluationIR:
    return ModelEvaluationIR(
        model_identity="credit.joblib",
        point=PointBindingIR(name="applicant", binding_kind="anchor"),
        output_name="decision",
    )


def test_logistic_encoder_emits_internal_affine_quantity_equation() -> None:
    assumption = SklearnLogisticRegressionEncoder().encode(_schema(), (_evaluation(),))[
        0
    ]
    atom = assumption.formula.expression

    assert isinstance(atom, AffineModelQuantityConstraintIR2)
    assert atom.quantity.quantity_kind is EnumModelQuantityKind.ORIENTED_DECISION_VALUE
    assert atom.evaluation == _evaluation()
    assert atom.expression.bias == 0.25
    assert [(term.feature, term.coefficient) for term in atom.expression.terms] == [
        ("income", 1.5),
        ("debt", -2.0),
    ]
    assert atom.metadata["native_probability_threshold"] == "0.5"
    assert atom.metadata["native_decision_threshold"] == "0"
    assert atom.metadata["threshold_source"] == "recognized_model_profile"


def test_default_factory_registers_logistic_regression_encoder() -> None:
    assumptions = ModelEncoderFactory().encode(_schema(), (_evaluation(),))
    assert isinstance(
        assumptions[0].formula.expression,
        AffineModelQuantityConstraintIR2,
    )


def test_logistic_encoder_rejects_unfitted_schema() -> None:
    schema = replace(_schema(), metadata={})

    with pytest.raises(MissingModelParameterError, match="fitted direct"):
        SklearnLogisticRegressionEncoder().encode(schema, (_evaluation(),))


def test_logistic_encoder_rejects_non_finite_parameters() -> None:
    with pytest.raises(UnsupportedModelParameterError, match="finite"):
        SklearnLogisticRegressionEncoder().encode(
            _schema(coefficient=math.inf),
            (_evaluation(),),
        )


def test_logistic_encoder_rejects_schema_without_native_decision_policy() -> None:
    schema = replace(
        _schema(),
        output_schema=ClassificationOutputSchema(
            label_dtype=EnumDataType.STRING,
            labels=("rejected", "approved"),
            probability_available=True,
        ),
    )

    with pytest.raises(UnsupportedModelParameterError, match="decision policy"):
        SklearnLogisticRegressionEncoder().encode(schema, (_evaluation(),))


@pytest.mark.parametrize(
    "model_type",
    [
        "Pipeline",
        "FixedThresholdClassifier",
        "TunedThresholdClassifierCV",
        "CalibratedClassifierCV",
        "CustomClassifierWrapper",
    ],
)
def test_initial_registry_rejects_wrappers(model_type: str) -> None:
    schema = replace(_schema(), model_type=model_type)

    with pytest.raises(UnsupportedModelEncoderError):
        ModelEncoderFactory().create(schema)
