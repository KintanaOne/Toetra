from __future__ import annotations

from toetra._compiler.ir.ir1.model_quantities import EnumModelQuantityKind
from toetra._compiler.ir.ir1.nodes import ModelEvaluationIR, PointBindingIR
from toetra._compiler.ir.ir2.model.affine import (
    AffineModelQuantityConstraintIR2,
    AffineOutputConstraintIR2,
)
from toetra._compiler.model_lowering.factory import ModelIRLoweringFactory
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.encoder.sklearn.linear import SklearnLinearRegressorEncoder
from toetra._models.encoder.sklearn.logistic import (
    SklearnLogisticRegressionEncoder,
)
from toetra._models.ir.affine import AffineModelIR
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema
from toetra._models.schema.output_schema import (
    BinaryClassificationDecisionPolicy,
    ClassificationOutputSchema,
)


def _evaluation(output_name: str) -> ModelEvaluationIR:
    return ModelEvaluationIR(
        model_identity="model.joblib",
        point=PointBindingIR(name="x", binding_kind="anchor"),
        output_name=output_name,
    )


def _regression_schema() -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features=(
            FeatureSchema(name="a", dtype=EnumDataType.FLOAT),
            FeatureSchema(name="b", dtype=EnumDataType.FLOAT),
        ),
        output_name="score",
        task="regression",
        metadata={
            "linear": {
                "coef": [1.5, -2.0],
                "intercept": 0.25,
                "feature_names": ["a", "b"],
            }
        },
    )


def _classification_schema() -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LogisticRegression",
        features=(
            FeatureSchema(name="income", dtype=EnumDataType.FLOAT),
            FeatureSchema(name="debt", dtype=EnumDataType.FLOAT),
        ),
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
                "coef": [[1.5, -2.0]],
                "intercept": [0.25],
                "feature_names": ["income", "debt"],
            }
        },
    )


def test_affine_regression_lowering_no_longer_reads_computational_metadata() -> None:
    schema = _regression_schema()
    schema_without_parameters = ModelSchema(
        framework=schema.framework,
        model_type=schema.model_type,
        features=schema.features,
        output_name=schema.output_name,
        task=schema.task,
        output_schema=schema.output_schema,
        metadata={},
    )
    model_ir = AffineModelIR(terms=(("a", 1.5), ("b", -2.0)), bias=0.25)

    assumption = ModelIRLoweringFactory().lower(
        model_ir,
        schema_without_parameters,
        (_evaluation("score"),),
    )[0]

    atom = assumption.formula.expression
    assert isinstance(atom, AffineOutputConstraintIR2)
    assert atom.expression.bias == 0.25
    assert [(term.feature, term.coefficient) for term in atom.expression.terms] == [
        ("a", 1.5),
        ("b", -2.0),
    ]


def test_regression_model_ir_lowering_is_identical_to_legacy_encoder() -> None:
    schema = _regression_schema()
    evaluation = _evaluation("score")
    model_ir = AffineModelIR(terms=(("a", 1.5), ("b", -2.0)), bias=0.25)

    modern = ModelIRLoweringFactory().lower(model_ir, schema, (evaluation,))
    legacy = SklearnLinearRegressorEncoder().encode(schema, (evaluation,))

    assert modern == legacy


def test_binary_logistic_model_ir_lowering_is_identical_to_legacy_encoder() -> None:
    schema = _classification_schema()
    evaluation = _evaluation("decision")
    model_ir = AffineModelIR(
        terms=(("income", 1.5), ("debt", -2.0)),
        bias=0.25,
    )

    modern = ModelIRLoweringFactory().lower(model_ir, schema, (evaluation,))
    legacy = SklearnLogisticRegressionEncoder().encode(schema, (evaluation,))

    assert modern == legacy
    atom = modern[0].formula.expression
    assert isinstance(atom, AffineModelQuantityConstraintIR2)
    assert atom.quantity.quantity_kind is EnumModelQuantityKind.ORIENTED_DECISION_VALUE
