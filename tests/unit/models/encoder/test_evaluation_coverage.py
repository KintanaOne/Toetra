from __future__ import annotations

import pytest

from toetra._compiler.ir.ir1.nodes import ModelEvaluationIR, PointBindingIR
from toetra._compiler.ir.ir2.enums import AssumptionSource
from toetra._compiler.ir.ir2.model.affine import (
    AffineExpressionIR2,
    AffineOutputConstraintIR2,
)
from toetra._compiler.ir.ir2.dsl.nodes import (
    AssumptionIR2,
    NNFFormulaIR2,
)
from toetra._language.vocabulary.operators import EnumComparisonOperator
from toetra._models.encoder.errors import InvalidModelAssumptionError
from toetra._models.encoder.base import (
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
