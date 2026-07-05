from __future__ import annotations

from dsl.ir.ir1.run_ir1 import run_ir

from test.fixtures.normalization.nnf.helpers import assert_is_nnf, normalizer, sexpr



def _run_ir1_then_nnf(source: str):
    ir1_tasks = run_ir(source)
    return normalizer().normalize_tasks(ir1_tasks)



def test_pipeline_check_at_implication_becomes_nnf():
    source = '''
model := "model.onnx"
target := MyTarget

[LOGIC]:
check_at x0 => x0.a <= 1 -> x0.b <= 2 using Z3
'''

    tasks = _run_ir1_then_nnf(source)

    assert len(tasks) == 1
    expr = tasks[0].query.expression

    assert sexpr(expr) == "OR(NOT(CMP(x0.a <= 1)), CMP(x0.b <= 2))"
    assert_is_nnf(expr)



def test_pipeline_check_at_demorgan_and_becomes_nnf():
    source = '''
model := "model.onnx"
target := MyTarget

[LOGIC]:
check_at x0 => NOT (x0.a <= 1 AND x0.b <= 2) using Z3
'''

    tasks = _run_ir1_then_nnf(source)

    assert len(tasks) == 1
    expr = tasks[0].query.expression

    assert sexpr(expr) == "OR(NOT(CMP(x0.a <= 1)), NOT(CMP(x0.b <= 2)))"
    assert_is_nnf(expr)



def test_pipeline_check_at_demorgan_or_becomes_nnf():
    source = '''
model := "model.onnx"
target := MyTarget

[LOGIC]:
check_at x0 => NOT (x0.a <= 1 OR x0.b <= 2) using Z3
'''

    tasks = _run_ir1_then_nnf(source)

    assert len(tasks) == 1
    expr = tasks[0].query.expression

    assert sexpr(expr) == "AND(NOT(CMP(x0.a <= 1)), NOT(CMP(x0.b <= 2)))"
    assert_is_nnf(expr)



def test_pipeline_at_scope_keeps_implicit_perturbation_binding_after_nnf():
    source = '''
model := "model.onnx"
target := MyTarget

[ROBUSTNESS]:
at x in neighborhood(L2, eps=0.01) => NOT (a <= 1 OR b <= 2) using Z3
'''

    tasks = _run_ir1_then_nnf(source)

    assert len(tasks) == 1
    task = tasks[0]
    expr = task.query.expression

    assert task.scope.kind == "local"
    assert task.scope.variables == {"x": "anchor", "x'": "perturbation"}
    assert sexpr(expr) == "AND(NOT(CMP(x'.a <= 1)), NOT(CMP(x'.b <= 2)))"
    assert_is_nnf(expr)



def test_pipeline_pairwise_scope_keeps_pairwise_binding_after_nnf():
    source = '''
model := "model.onnx"
target := MyTarget

[MONOTONICITY]:
x ~ x' in neighborhood(L2, eps=0.01) => NOT (a <= 1 AND b <= 2) using Z3
'''

    tasks = _run_ir1_then_nnf(source)

    assert len(tasks) == 1
    task = tasks[0]
    expr = task.query.expression

    assert task.scope.kind == "pairwise"
    assert task.scope.variables == {"x": "anchor", "x'": "perturbation"}
    assert sexpr(expr) == "OR(NOT(CMP(x'.a <= 1)), NOT(CMP(x'.b <= 2)))"
    assert_is_nnf(expr)
