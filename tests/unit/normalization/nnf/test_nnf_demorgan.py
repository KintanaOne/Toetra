from __future__ import annotations

from toetra._compiler.ir.ir1.nodes import AndIR, NotIR, OrIR

from tests.support.normalization import (
    assert_is_nnf,
    cmp,
    normalizer,
    sexpr,
)


def test_demorgan_not_and_becomes_or_of_negated_operands():
    expr = NotIR(
        AndIR(
            operands=[
                cmp("a", 1),
                cmp("b", 2),
            ]
        )
    )

    got = normalizer().normalize_expr(expr)

    assert sexpr(got) == "OR(NOT(CMP(x0.a <= 1)), NOT(CMP(x0.b <= 2)))"
    assert_is_nnf(got)


def test_demorgan_not_or_becomes_and_of_negated_operands():
    expr = NotIR(
        OrIR(
            operands=[
                cmp("a", 1),
                cmp("b", 2),
            ]
        )
    )

    got = normalizer().normalize_expr(expr)

    assert sexpr(got) == "AND(NOT(CMP(x0.a <= 1)), NOT(CMP(x0.b <= 2)))"
    assert_is_nnf(got)


def test_double_negation_is_eliminated():
    expr = NotIR(NotIR(cmp("a", 1)))

    got = normalizer().normalize_expr(expr)

    assert sexpr(got) == "CMP(x0.a <= 1)"
    assert_is_nnf(got)


def test_complex_demorgan_expression_is_nnf():
    expr = NotIR(
        OrIR(
            operands=[
                AndIR(operands=[cmp("a", 1), cmp("b", 2)]),
                NotIR(cmp("c", 3)),
            ]
        )
    )

    got = normalizer().normalize_expr(expr)

    assert sexpr(got) == (
        "AND(OR(NOT(CMP(x0.a <= 1)), NOT(CMP(x0.b <= 2))), CMP(x0.c <= 3))"
    )
    assert_is_nnf(got)
