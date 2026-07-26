from __future__ import annotations

import pytest

from toetra._compiler.ir.ir1.nodes import NotIR
from toetra._language.vocabulary.operators import EnumComparisonOperator

from tests.support.normalization import (
    assert_is_nnf,
    cmp,
    normalizer,
    sexpr,
)


@pytest.mark.parametrize(
    "operator, expected_symbol",
    [
        (EnumComparisonOperator.EQ, "=="),
        (EnumComparisonOperator.NEQ, "!="),
        (EnumComparisonOperator.LT, "<"),
        (EnumComparisonOperator.LTE, "<="),
        (EnumComparisonOperator.GT, ">"),
        (EnumComparisonOperator.GTE, ">="),
    ],
)
def test_comparison_operator_is_preserved_under_leaf_negation(
    operator, expected_symbol
):
    expr = NotIR(cmp("a", 1, op=operator))

    got = normalizer().normalize_expr(expr)

    assert sexpr(got) == f"NOT(CMP(x0.a {expected_symbol} 1))"
    assert_is_nnf(got)
