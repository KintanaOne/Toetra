from dsl.ir.ir1.nodes import ComparisonIR
from dsl.ir.ir1.run_ir1 import run_ir
from dsl.language.vocabulary.operators import EnumComparisonOperator
from dsl.semantic.types.enums import EnumDataType


def test_target_ref_lowers_to_model_output_in_ir1():
    code = """
    model := "model.onnx"
    target := MyTarget

    [BOUND]:
    check_at x0 => target <= 10
    """

    tasks = run_ir(code)

    expr = tasks[0].query.expression

    assert isinstance(expr, ComparisonIR)
    assert expr.entity == "_model"
    assert expr.feature == "MyTarget"
    assert expr.op == EnumComparisonOperator.LTE
    assert expr.value == 10
    assert expr.feature_dtype is None
    assert expr.value_dtype is not None
    assert expr.value_dtype == EnumDataType.INT
