from dsl.ir.ir1.nodes import ComparisonIR
from dsl.ir.ir2.dsl.nodes import NNFFormulaIR2
from dsl.ir.ir2.run_ir2 import run_ir2
from dsl.language.vocabulary.operators import EnumComparisonOperator


def test_target_ref_survives_to_ir2_spec_formula():
    code = """
    model := "model.onnx"
    target := MyTarget

    [BOUND]:
    check_at x0 => target <= 10 using Z3
    """

    tasks = run_ir2(code)

    assert len(tasks) == 1

    task = tasks[0]

    assert isinstance(task.spec_formula, NNFFormulaIR2)

    expr = task.spec_formula.expression

    assert isinstance(expr, ComparisonIR)
    assert expr.entity == "_model"
    assert expr.feature == "MyTarget"
    assert expr.op == EnumComparisonOperator.LTE
    assert expr.value == 10
    assert expr.feature_dtype is None
