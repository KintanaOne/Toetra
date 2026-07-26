from __future__ import annotations

from toetra._compiler.ir.ir1.nodes import ModelEvaluationIR
from toetra._compiler.ir.ir2.builder import IR2Builder
from toetra._compiler.ir.ir2.enums import AssumptionSource
from toetra._compiler.ir.ir2.guardrails.model_output import (
    MODEL_EVALUATION_DISCONNECTED,
    MODEL_EVALUATION_DUPLICATE,
    MODEL_EVALUATION_MISSING,
)
from toetra._compiler.ir.ir2.model.affine import (
    AffineExpressionIR2,
    AffineOutputConstraintIR2,
)
from toetra._compiler.ir.ir2.nodes import AssumptionIR2, NNFFormulaIR2
from toetra._compiler.ir.ir2.run_ir2 import run_ir2
from toetra._compiler.ir.ir1.run_ir1 import run_ir
from toetra._compiler.ir.normalization.nnf import NNFNormalizer
from toetra._language.vocabulary.operators import EnumComparisonOperator


def _codes(task) -> set[str]:
    return {diagnostic.code for diagnostic in task.diagnostics}


def _equation(evaluation: ModelEvaluationIR) -> AssumptionIR2:
    return AssumptionIR2(
        source=AssumptionSource.MODEL,
        formula=NNFFormulaIR2(
            expression=AffineOutputConstraintIR2(
                output_entity="_model",
                output_feature=evaluation.target_name,
                op=EnumComparisonOperator.EQ,
                expression=AffineExpressionIR2(terms=(), bias=0.0),
                evaluation=evaluation,
            )
        ),
    )


def test_missing_model_equation_is_reported_per_evaluation() -> None:
    task = run_ir2("""
        model := "linear.joblib"
        target := score

        [BOUND]:
        forall x0 => target[x0] <= 1.0
        """)[0]

    assert MODEL_EVALUATION_MISSING in _codes(task)


def test_unrequested_model_equation_is_reported_as_disconnected() -> None:
    source = """
    model := "linear.joblib"
    target := score

    [LOGIC]:
    forall x0 => x0.a <= 1.0
    """
    ir1_task = NNFNormalizer().normalize_tasks(run_ir(source))[0]
    point = ir1_task.scope.points[0]
    evaluation = ModelEvaluationIR("linear.joblib", point, "score")

    task = IR2Builder().build(ir1_task, assumptions=(_equation(evaluation),))

    assert MODEL_EVALUATION_DISCONNECTED in _codes(task)


def test_duplicate_model_equations_are_reported_per_evaluation() -> None:
    source = """
    model := "linear.joblib"
    target := score

    [BOUND]:
    forall x0 => target[x0] <= 1.0
    """
    ir1_task = NNFNormalizer().normalize_tasks(run_ir(source))[0]
    point = ir1_task.scope.points[0]
    evaluation = ModelEvaluationIR("linear.joblib", point, "score")
    equation = _equation(evaluation)

    task = IR2Builder().build(ir1_task, assumptions=(equation, equation))

    assert MODEL_EVALUATION_DUPLICATE in _codes(task)
