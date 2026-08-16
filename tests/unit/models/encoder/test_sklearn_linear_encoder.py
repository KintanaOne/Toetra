from __future__ import annotations

from toetra._compiler.ir.ir1.nodes import (
    AttributeExpressionIR,
    ComparisonIR,
    ConstantExpressionIR,
    ModelEvaluationIR,
    PointBindingIR,
    QueryIR,
    ScopeIR,
    VerificationTask,
)
from toetra._compiler.ir.ir2.builder import IR2Builder
from toetra._compiler.ir.ir2.context import IR2BuildContext
from toetra._compiler.ir.ir2.enums import NormalFormKind
from toetra._compiler.ir.ir2.dsl.nodes import DNFFormulaIR2
from toetra._compiler.ir.ir2.model.affine import AffineOutputConstraintIR2
from toetra._language.vocabulary.operators import EnumComparisonOperator
from toetra._language.vocabulary.properties import EnumProperty
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.encoder.factory import ModelEncoderFactory
from toetra._models.encoder.sklearn.linear import SklearnLinearRegressorEncoder
from toetra._models.encoder.context import ModelEncodingContext
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema


def _schema() -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features={
            "a": FeatureSchema(name="a", dtype=EnumDataType.FLOAT),
            "b": FeatureSchema(name="b", dtype=EnumDataType.FLOAT),
        },
        target="score",
        task="regression",
        metadata={
            "linear": {
                "coef": [1.5, -2.0],
                "intercept": 0.25,
                "feature_names": ["a", "b"],
            }
        },
    )


def _point(name: str = "x") -> PointBindingIR:
    return PointBindingIR(name=name, binding_kind="anchor")


def _evaluation(name: str = "x") -> ModelEvaluationIR:
    return ModelEvaluationIR(
        model_identity="model.pkl",
        point=_point(name),
        target_name="score",
    )


def _scope() -> ScopeIR:
    point = _point()
    return ScopeIR(
        kind="pointwise",
        variables={"x": "anchor"},
        neighborhood=None,
        domain=None,
        points=(point,),
        default_point=point,
    )


def test_sklearn_linear_regressor_encoder_emits_model_output_assumption() -> None:
    evaluation = _evaluation()
    assumptions = SklearnLinearRegressorEncoder().encode(_schema(), (evaluation,))

    assert len(assumptions) == 1

    atom = assumptions[0].formula.expression

    assert isinstance(atom, AffineOutputConstraintIR2)
    assert atom.output_entity == "_model"
    assert atom.output_feature == "score"
    assert atom.evaluation == evaluation
    assert atom.op is EnumComparisonOperator.EQ
    assert atom.expression.bias == 0.25
    assert [(t.entity, t.feature, t.coefficient) for t in atom.expression.terms] == [
        ("x", "a", 1.5),
        ("x", "b", -2.0),
    ]
    assert all(term.point == evaluation.point for term in atom.expression.terms)


def test_default_factory_registers_sklearn_linear_regression_encoder() -> None:
    assumptions = ModelEncoderFactory().encode(_schema(), (_evaluation(),))

    assert len(assumptions) == 1
    assert isinstance(assumptions[0].formula.expression, AffineOutputConstraintIR2)


def test_model_output_assumption_survives_ir2_aggregation_and_dnf() -> None:
    assumptions = ModelEncoderFactory().encode(_schema(), (_evaluation(),))
    spec = ComparisonIR(
        left=AttributeExpressionIR(entity="x", feature="a", point=_point()),
        op=EnumComparisonOperator.LTE,
        right=ConstantExpressionIR(value=10, dtype=EnumDataType.INT),
    )
    task = VerificationTask(
        property_type=EnumProperty.LOGIC,
        scope=_scope(),
        query=QueryIR(expression=spec),
        backend=None,
    )

    ir2_task = IR2Builder().build(
        task,
        assumptions=assumptions,
        context=IR2BuildContext(preferred_normal_form=NormalFormKind.DNF),
    )

    assert ir2_task.requirements.requires_model_assertions is True
    assert ir2_task.requirements.requires_numeric_comparisons is True
    assert isinstance(ir2_task.verification_condition, DNFFormulaIR2)

    literals = ir2_task.verification_condition.terms[0].literals
    assert any(
        isinstance(literal.atom, AffineOutputConstraintIR2) for literal in literals
    )


def test_encoder_can_explicitly_disable_model_constraints() -> None:
    assumptions = ModelEncoderFactory().encode(
        _schema(),
        (_evaluation(),),
        context=ModelEncodingContext(include_model_constraints=False),
    )

    assert assumptions == ()


def test_encoder_emits_nothing_when_no_output_is_requested() -> None:
    assert ModelEncoderFactory().encode(_schema(), ()) == ()
