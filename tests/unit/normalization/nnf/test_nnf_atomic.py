from __future__ import annotations

from toetra._compiler.ir.ir1.nodes import NotIR, ProblemIR

from tests.support.normalization import (
    assert_is_nnf,
    cmp,
    normalizer,
    problem,
    sexpr,
)


def test_atomic_comparison_is_preserved():
    expr = cmp("a", 1)

    got = normalizer().normalize_expr(expr)

    assert got == expr
    assert sexpr(got) == "CMP(x0.a <= 1)"
    assert_is_nnf(got)


def test_not_comparison_is_valid_nnf_leaf_negation():
    expr = NotIR(cmp("a", 1))

    got = normalizer().normalize_expr(expr)

    assert sexpr(got) == "NOT(CMP(x0.a <= 1))"
    assert_is_nnf(got)


def test_problem_ir_is_preserved_as_atomic_predicate():
    expr = problem()

    got = normalizer().normalize_expr(expr)

    assert isinstance(got, ProblemIR)
    assert sexpr(got) == "PROBLEM(CLASSIFICATION.EQUAL)"
    assert_is_nnf(got)


def test_not_problem_ir_is_valid_nnf_leaf_negation():
    expr = NotIR(problem())

    got = normalizer().normalize_expr(expr)

    assert sexpr(got) == "NOT(PROBLEM(CLASSIFICATION.EQUAL))"
    assert_is_nnf(got)
