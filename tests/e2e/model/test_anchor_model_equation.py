from __future__ import annotations

from toetra._compiler.ir.ir2.enums import AssumptionSource
from toetra._compiler.ir.ir2.model.affine import AffineOutputConstraintIR2
from toetra._compiler.ir.ir2.run_ir2 import run_ir2_with_model_schema
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
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
                "coef": [1.0, 2.0],
                "intercept": 3.0,
                "feature_names": ["a", "b"],
            }
        },
    )


def test_mb_eval_006_anchor_facts_and_model_equation_share_point_identity() -> None:
    task = run_ir2_with_model_schema(
        """
        model := "linear.joblib"
        target := score

        anchor customer := {
            a: 1.0,
            b: 2.0
        }

        [BOUND]:
        check_at customer => target <= 10.0
        """,
        schema=_schema(),
    )[0]

    model_assumptions = [
        assumption
        for assumption in task.assumptions
        if assumption.source is AssumptionSource.MODEL
    ]
    anchor_assumptions = [
        assumption
        for assumption in task.assumptions
        if assumption.source is AssumptionSource.SCOPE
    ]

    assert len(model_assumptions) == 1
    assert len(anchor_assumptions) == 2

    equation = model_assumptions[0].formula.expression
    assert isinstance(equation, AffineOutputConstraintIR2)
    assert equation.evaluation is not None
    assert equation.evaluation.point.name == "customer"
    assert all(
        term.point == equation.evaluation.point for term in equation.expression.terms
    )

    assert {assumption.metadata["point"] for assumption in anchor_assumptions} == {
        "customer"
    }
    assert all(
        assumption.metadata["binding_kind"] == "inline_anchor"
        for assumption in anchor_assumptions
    )
