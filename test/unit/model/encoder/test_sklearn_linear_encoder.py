from __future__ import annotations

from dsl.ir.ir1.nodes import ComparisonIR, QueryIR, ScopeIR, VerificationTask
from dsl.ir.ir2.builder import IR2Builder
from dsl.ir.ir2.context import IR2BuildContext
from dsl.ir.ir2.enums import NormalFormKind
from dsl.ir.ir2.nodes import DNFFormulaIR2, AffineOutputConstraintIR2
from dsl.language.vocabulary.operators import EnumComparisonOperator
from dsl.language.vocabulary.properties import EnumProperty
from dsl.semantic.types.enums import EnumDataType
from model.detector.model_framework import EnumModelFramework
from model.encoder import ModelEncoderFactory, SklearnLinearRegressorEncoder
from model.schema.feature_schema import FeatureSchema
from model.schema.model_schema import ModelSchema


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


def _scope() -> ScopeIR:
    return ScopeIR(
        kind="pointwise",
        variables={"x": "anchor"},
        neighborhood=None,
        domain=None,
    )


def test_sklearn_linear_regressor_encoder_emits_model_output_assumption() -> None:
    assumptions = SklearnLinearRegressorEncoder().encode(_schema(), _scope())

    assert len(assumptions) == 1

    atom = assumptions[0].formula.expression

    assert isinstance(atom, AffineOutputConstraintIR2)
    assert atom.output_entity == "_model"
    assert atom.output_feature == "score"
    assert atom.op is EnumComparisonOperator.EQ
    assert atom.expression.bias == 0.25
    assert [(t.entity, t.feature, t.coefficient) for t in atom.expression.terms] == [
        ("x", "a", 1.5),
        ("x", "b", -2.0),
    ]


def test_default_factory_registers_sklearn_linear_regression_encoder() -> None:
    assumptions = ModelEncoderFactory().encode(_schema(), _scope())

    assert len(assumptions) == 1
    assert isinstance(assumptions[0].formula.expression, AffineOutputConstraintIR2)


def test_model_output_assumption_survives_ir2_aggregation_and_dnf() -> None:
    assumptions = ModelEncoderFactory().encode(_schema(), _scope())
    spec = ComparisonIR(
        entity="x",
        feature="a",
        op=EnumComparisonOperator.LTE,
        value=10,
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
