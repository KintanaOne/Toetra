from toetra._compiler.ir.ir1.nodes import ModelEvaluationIR, PointBindingIR
from toetra._compiler.ir.ir2.model.affine import (
    AffineExpressionIR2,
    AffineOutputConstraintIR2,
    AffineTermIR2,
)
from toetra._compiler.ir.ir2.nodes import NNFFormulaIR2
from toetra._compiler.ir.ir2.pretty import pretty_formula
from toetra._language.vocabulary.operators import EnumComparisonOperator


def test_point_aware_affine_equation_pretty_prints_indexed_target() -> None:
    point = PointBindingIR(name="x0", binding_kind="universal")
    evaluation = ModelEvaluationIR("linear.joblib", point, "score")
    equation = AffineOutputConstraintIR2(
        output_entity="_model",
        output_feature="score",
        op=EnumComparisonOperator.EQ,
        expression=AffineExpressionIR2(
            terms=(
                AffineTermIR2(
                    entity="x0",
                    feature="a",
                    coefficient=2.0,
                    point=point,
                ),
            ),
            bias=1.0,
        ),
        evaluation=evaluation,
    )

    assert "target[x0] == 2.0*x0.a + 1.0" in pretty_formula(
        NNFFormulaIR2(expression=equation)
    )
