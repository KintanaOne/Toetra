from __future__ import annotations

from toetra._compiler.ir.ir1.nodes import ImplyIR, NotIR

from tests.support.normalization import (
    assert_is_nnf,
    assert_no_implication,
    cmp,
    normalizer,
    sexpr,
)


def test_implication_is_lowered_to_or_not_left_right():
    expr = ImplyIR(
        left=cmp("a", 1),
        right=cmp("b", 2),
    )

    got = normalizer().normalize_expr(expr)

    assert sexpr(got) == "OR(NOT(CMP(x0.a <= 1)), CMP(x0.b <= 2))"
    assert_no_implication(got)
    assert_is_nnf(got)


def test_negated_implication_is_lowered_to_and_left_not_right():
    expr = NotIR(
        ImplyIR(
            left=cmp("a", 1),
            right=cmp("b", 2),
        )
    )

    got = normalizer().normalize_expr(expr)

    assert sexpr(got) == "AND(CMP(x0.a <= 1), NOT(CMP(x0.b <= 2)))"
    assert_no_implication(got)
    assert_is_nnf(got)


def test_nested_implication_is_removed_everywhere():
    expr = ImplyIR(
        left=cmp("a", 1),
        right=ImplyIR(
            left=cmp("b", 2),
            right=cmp("c", 3),
        ),
    )

    got = normalizer().normalize_expr(expr)

    assert "IMPLY" not in sexpr(got)
    assert_no_implication(got)
    assert_is_nnf(got)
