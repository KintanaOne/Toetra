from __future__ import annotations

from toetra._compiler.ir.ir1.run_ir1 import run_ir
from toetra._compiler.ir.ir1.nodes import NotIR, ProblemIR

from test.fixtures.normalization.nnf.helpers import assert_is_nnf, normalizer, sexpr


def _run_ir1_then_nnf(source: str):
    ir1_tasks = run_ir(source)
    return normalizer().normalize_tasks(ir1_tasks)


def test_pipeline_problem_predicate_is_atomic_under_negation():
    source = """
model := "model.onnx"
target := MyTarget

[ROBUSTNESS]:
forall x0, x1 => NOT CLASSIFICATION.EQUAL() using Z3
"""

    tasks = _run_ir1_then_nnf(source)

    assert len(tasks) == 1
    expr = tasks[0].query.expression

    assert isinstance(expr, NotIR)
    assert isinstance(expr.operand, ProblemIR)
    assert sexpr(expr) == "NOT(PROBLEM(CLASSIFICATION.EQUAL))"
    assert_is_nnf(expr)


def test_pipeline_problem_predicate_inside_implication_is_normalized():
    source = """
model := "model.onnx"
target := MyTarget

[ROBUSTNESS]:
forall x0, x1 => x0.a <= 1 -> CLASSIFICATION.EQUAL() using Z3
"""

    tasks = _run_ir1_then_nnf(source)

    assert len(tasks) == 1
    expr = tasks[0].query.expression

    assert sexpr(expr) == "OR(NOT(CMP(x0.a <= 1)), PROBLEM(CLASSIFICATION.EQUAL))"
    assert_is_nnf(expr)
