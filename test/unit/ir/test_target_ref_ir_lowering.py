from dsl.ir.ir1.nodes import (
    ComparisonIR,
    ConstantExpressionIR,
    TargetExpressionIR,
)
from dsl.ir.ir1.run_ir1 import run_ir
from dsl.language.vocabulary.operators import EnumComparisonOperator
from dsl.semantic.types.enums import EnumDataType


def test_target_ref_lowers_to_model_output_in_ir1():
    code = """
    model := "model.onnx"
    target := MyTarget

    [BOUND]:
    forall x0 => target <= 10
    """

    expr = run_ir(code)[0].query.expression

    assert isinstance(expr, ComparisonIR)
    assert isinstance(expr.left, TargetExpressionIR)
    assert expr.left.entity == "_model"
    assert expr.left.feature == "MyTarget"
    assert expr.left.dtype is None
    assert expr.op is EnumComparisonOperator.LTE
    assert isinstance(expr.right, ConstantExpressionIR)
    assert expr.right.value == 10
    assert expr.right.dtype is EnumDataType.INT
