from __future__ import annotations

import pytest

from dsl.ir.ir1.run_ir1 import run_ir

from test.fixtures.normalization.nnf.helpers import (
    assert_is_nnf,
    assert_quantifier_scope,
    assert_scope_domain_values,
    normalizer,
    sexpr,
)


def _run_ir1_then_nnf(source: str):
    ir1_tasks = run_ir(source)
    return normalizer().normalize_tasks(ir1_tasks)


def test_pipeline_forall_demorgan_keeps_symbolic_binding_after_nnf():
    source = """
model := "model.onnx"
target := MyTarget

[LOGIC]:
forall => NOT (a <= 1 AND b <= 2) using Z3
"""

    tasks = _run_ir1_then_nnf(source)

    assert len(tasks) == 1
    task = tasks[0]

    assert_quantifier_scope(task)
    assert sexpr(task.query.expression) == (
        "OR(NOT(CMP(_x.a <= 1)), NOT(CMP(_x.b <= 2)))"
    )
    assert_is_nnf(task.query.expression)


def test_pipeline_exists_implication_keeps_symbolic_binding_after_nnf():
    source = """
model := "model.onnx"
target := MyTarget

[LOGIC]:
exists => a <= 1 -> b <= 2 using Z3
"""

    tasks = _run_ir1_then_nnf(source)

    assert len(tasks) == 1
    task = tasks[0]

    assert_quantifier_scope(task)
    assert sexpr(task.query.expression) == "OR(NOT(CMP(_x.a <= 1)), CMP(_x.b <= 2))"
    assert_is_nnf(task.query.expression)


def test_pipeline_forall_with_domain_preserves_domain_and_symbolic_binding():
    source = """
model := "model.onnx"
target := MyTarget

[LOGIC]:
forall with Segment("A", "B") => NOT (a <= 1 OR b <= 2) using Z3
"""

    tasks = _run_ir1_then_nnf(source)

    assert len(tasks) == 1
    task = tasks[0]

    assert_quantifier_scope(task)
    assert_scope_domain_values(task, "Segment", ["A", "B"])
    assert sexpr(task.query.expression) == (
        "AND(NOT(CMP(_x.a <= 1)), NOT(CMP(_x.b <= 2)))"
    )
    assert_is_nnf(task.query.expression)


@pytest.mark.parametrize(
    "token, expected_query",
    [
        ("∀", "OR(NOT(CMP(_x.a <= 1)), NOT(CMP(_x.b <= 2)))"),
        ("∃", "OR(NOT(CMP(_x.a <= 1)), NOT(CMP(_x.b <= 2)))"),
    ],
)
def test_pipeline_unicode_quantifiers_are_supported_if_grammar_exposes_them(
    token: str,
    expected_query: str,
):
    source = f"""
model := "model.onnx"
target := MyTarget

[LOGIC]:
{token} => NOT (a <= 1 AND b <= 2) using Z3
"""

    tasks = _run_ir1_then_nnf(source)

    assert len(tasks) == 1
    task = tasks[0]

    assert_quantifier_scope(task)
    assert sexpr(task.query.expression) == expected_query
    assert_is_nnf(task.query.expression)
