from __future__ import annotations

from toetra._compiler.ir.ir1.run_ir1 import run_ir

from test.fixtures.normalization.nnf.helpers import assert_is_nnf, normalizer, sexpr


def _run_ir1_then_nnf(source: str):
    ir1_tasks = run_ir(source)
    return normalizer().normalize_tasks(ir1_tasks)


def test_pipeline_check_at_implication_becomes_nnf():
    source = """
model := "model.onnx"
target := MyTarget

[LOGIC]:
forall x0 => x0.a <= 1 -> x0.b <= 2 using Z3
"""

    tasks = _run_ir1_then_nnf(source)

    assert len(tasks) == 1
    expr = tasks[0].query.expression

    assert sexpr(expr) == "OR(NOT(CMP(x0.a <= 1)), CMP(x0.b <= 2))"
    assert_is_nnf(expr)


def test_pipeline_check_at_demorgan_and_becomes_nnf():
    source = """
model := "model.onnx"
target := MyTarget

[LOGIC]:
forall x0 => NOT (x0.a <= 1 AND x0.b <= 2) using Z3
"""

    tasks = _run_ir1_then_nnf(source)

    assert len(tasks) == 1
    expr = tasks[0].query.expression

    assert sexpr(expr) == "OR(NOT(CMP(x0.a <= 1)), NOT(CMP(x0.b <= 2)))"
    assert_is_nnf(expr)


def test_pipeline_check_at_demorgan_or_becomes_nnf():
    source = """
model := "model.onnx"
target := MyTarget

[LOGIC]:
forall x0 => NOT (x0.a <= 1 OR x0.b <= 2) using Z3
"""

    tasks = _run_ir1_then_nnf(source)

    assert len(tasks) == 1
    expr = tasks[0].query.expression

    assert sexpr(expr) == "AND(NOT(CMP(x0.a <= 1)), NOT(CMP(x0.b <= 2)))"
    assert_is_nnf(expr)


def test_pipeline_quantifier_scope_keeps_symbolic_binding_after_nnf():
    source = """
model := "model.onnx"
target := MyTarget

[ROBUSTNESS]:
forall x1 => NOT (a <= 1 OR b <= 2) using Z3
"""

    tasks = _run_ir1_then_nnf(source)

    assert len(tasks) == 1
    task = tasks[0]
    expr = task.query.expression

    assert task.scope.kind == "quantifier"
    assert task.scope.variables == {"x1": "symbolic"}
    assert sexpr(expr) == "AND(NOT(CMP(x1.a <= 1)), NOT(CMP(x1.b <= 2)))"
    assert_is_nnf(expr)


def test_pipeline_two_point_scope_keeps_explicit_bindings_after_nnf():
    source = """
model := "model.onnx"
target := MyTarget

[MONOTONICITY]:
forall x0, x1 => NOT (x1.a <= 1 AND x1.b <= 2) using Z3
"""

    tasks = _run_ir1_then_nnf(source)

    assert len(tasks) == 1
    task = tasks[0]
    expr = task.query.expression

    assert task.scope.kind == "quantifier"
    assert task.scope.variables == {"x0": "symbolic", "x1": "symbolic"}
    assert sexpr(expr) == "OR(NOT(CMP(x1.a <= 1)), NOT(CMP(x1.b <= 2)))"
    assert_is_nnf(expr)
