from __future__ import annotations

from dsl.ir.ir1.nodes import AndIR, DomainIR, NotIR, ScopeIR

from test.fixtures.normalization.nnf.helpers import (
    assert_is_nnf,
    assert_quantifier_scope,
    assert_scope_domain_values,
    cmp,
    normalizer,
    sexpr,
    task_with_expr,
)


def test_normalize_task_preserves_quantifier_scope_and_domain():
    task = task_with_expr(
        NotIR(
            AndIR(
                operands=[
                    cmp("a", 1, entity="_x"),
                    cmp("b", 2, entity="_x"),
                ]
            )
        )
    )
    task.scope = ScopeIR(
        kind="quantifier",
        variables={"_x": "symbolic"},
        neighborhood=None,
        domain=DomainIR(name="Segment", args={"values": ["A", "B"]}),
    )

    got = normalizer().normalize_task(task)

    assert_quantifier_scope(got)
    assert_scope_domain_values(got, "Segment", ["A", "B"])
    assert sexpr(got.query.expression) == (
        "OR(NOT(CMP(_x.a <= 1)), NOT(CMP(_x.b <= 2)))"
    )
    assert_is_nnf(got.query.expression)
