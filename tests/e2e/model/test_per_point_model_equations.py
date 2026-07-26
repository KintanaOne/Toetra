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
                "coef": [1.5, -2.0],
                "intercept": 0.25,
                "feature_names": ["a", "b"],
            }
        },
    )


def _model_equations(source: str) -> tuple[AffineOutputConstraintIR2, ...]:
    task = run_ir2_with_model_schema(source, schema=_schema())[0]
    equations = []
    for assumption in task.assumptions:
        if assumption.source is not AssumptionSource.MODEL:
            continue
        expression = assumption.formula.expression
        assert isinstance(expression, AffineOutputConstraintIR2)
        equations.append(expression)
    return tuple(equations)


def test_mb_eval_001_only_referenced_point_gets_one_equation() -> None:
    equations = _model_equations("""
        model := "linear.joblib"
        target := score

        [BOUND]:
        forall x0 => target[x0] <= 1.0
        """)

    assert len(equations) == 1
    assert equations[0].evaluation is not None
    assert equations[0].evaluation.point.name == "x0"


def test_mb_eval_002_repeated_target_reference_is_deduplicated() -> None:
    equations = _model_equations("""
        model := "linear.joblib"
        target := score

        [LOGIC]:
        forall x0 => target[x0] <= target[x0] + 0.1
        """)

    assert len(equations) == 1
    assert equations[0].evaluation is not None
    assert equations[0].evaluation.point.name == "x0"


def test_mb_eval_003_two_referenced_points_get_two_equations() -> None:
    equations = _model_equations("""
        model := "linear.joblib"
        target := score

        [MONOTONICITY]:
        forall x0, x1 => target[x0] <= target[x1]
        """)

    assert len(equations) == 2
    assert [
        equation.evaluation.point.name for equation in equations if equation.evaluation
    ] == [
        "x0",
        "x1",
    ]
    assert equations[0].evaluation != equations[1].evaluation


def test_mb_eval_004_equations_share_coefficients_and_intercept() -> None:
    equations = _model_equations("""
        model := "linear.joblib"
        target := score

        [MONOTONICITY]:
        forall x0, x1 => target[x0] <= target[x1]
        """)

    assert len(equations) == 2
    assert equations[0].expression.bias == equations[1].expression.bias == 0.25
    assert [term.coefficient for term in equations[0].expression.terms] == [1.5, -2.0]
    assert [term.coefficient for term in equations[1].expression.terms] == [1.5, -2.0]
    assert [term.entity for term in equations[0].expression.terms] == ["x0", "x0"]
    assert [term.entity for term in equations[1].expression.terms] == ["x1", "x1"]
    first_evaluation = equations[0].evaluation
    second_evaluation = equations[1].evaluation
    assert first_evaluation is not None
    assert second_evaluation is not None
    assert all(
        term.point == first_evaluation.point for term in equations[0].expression.terms
    )
    assert all(
        term.point == second_evaluation.point for term in equations[1].expression.terms
    )
