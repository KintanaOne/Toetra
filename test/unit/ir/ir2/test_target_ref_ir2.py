from toetra._compiler.ir.ir1.nodes import (
    ComparisonIR,
    ConstantExpressionIR,
    TargetExpressionIR,
)
from toetra._compiler.ir.ir2.nodes import NNFFormulaIR2
from toetra._compiler.ir.ir2.run_ir2 import run_ir2
from toetra._language.vocabulary.operators import EnumComparisonOperator


def test_target_ref_survives_to_ir2_spec_formula():
    code = """
    model := "model.onnx"
    target := MyTarget

    [BOUND]:
    forall x0 => target <= 10 using Z3
    """

    task = run_ir2(code)[0]
    assert isinstance(task.spec_formula, NNFFormulaIR2)

    expr = task.spec_formula.expression
    assert isinstance(expr, ComparisonIR)
    assert isinstance(expr.left, TargetExpressionIR)
    assert expr.left.entity == "_model"
    assert expr.left.feature == "MyTarget"
    assert expr.left.dtype is None
    assert expr.op == EnumComparisonOperator.LTE
    assert isinstance(expr.right, ConstantExpressionIR)
    assert expr.right.value == 10
