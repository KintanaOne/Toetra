from __future__ import annotations

import pytest

from dsl.ir.ir1.nodes import ModelEvaluationIR, PointBindingIR
from dsl.ir.ir2.enums import AssumptionSource
from dsl.ir.ir2.model.affine import (
    AffineExpressionIR2,
    AffineOutputConstraintIR2,
)
from dsl.ir.ir2.nodes import AssumptionIR2, NNFFormulaIR2
from dsl.language.vocabulary.operators import EnumComparisonOperator
from model.encoder import (
    InvalidModelAssumptionError,
    validate_model_assumptions,
    validate_model_evaluation_coverage,
)


def _evaluation(name: str) -> ModelEvaluationIR:
    return ModelEvaluationIR(
        model_identity="model.joblib",
        point=PointBindingIR(name=name, binding_kind="universal"),
        target_name="score",
    )


def _assumption(evaluation: ModelEvaluationIR) -> AssumptionIR2:
    return AssumptionIR2(
        source=AssumptionSource.MODEL,
        formula=NNFFormulaIR2(
            expression=AffineOutputConstraintIR2(
                output_entity="_model",
                output_feature="score",
                op=EnumComparisonOperator.EQ,
                expression=AffineExpressionIR2(terms=(), bias=0.0),
                evaluation=evaluation,
            )
        ),
    )


def test_model_encoder_boundary_rejects_duplicate_evaluation_equations() -> None:
    evaluation = _evaluation("x0")

    with pytest.raises(InvalidModelAssumptionError, match="more than one constraint"):
        validate_model_assumptions((_assumption(evaluation), _assumption(evaluation)))


def test_coverage_rejects_missing_requested_evaluation() -> None:
    evaluation = _evaluation("x0")

    with pytest.raises(InvalidModelAssumptionError, match="did not emit"):
        validate_model_evaluation_coverage((), (evaluation,))


def test_coverage_rejects_unrequested_equation() -> None:
    evaluation = _evaluation("x0")

    with pytest.raises(InvalidModelAssumptionError, match="unrequested"):
        validate_model_evaluation_coverage((_assumption(evaluation),), ())
