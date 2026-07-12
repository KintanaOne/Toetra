from __future__ import annotations
from dsl.ir.ir1.nodes import DomainEntryIR, FiniteSetDomainIR, SymbolLiteralIR

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
                    cmp("a", 1, entity="x0"),
                    cmp("b", 2, entity="x0"),
                ]
            )
        )
    )
    task.scope = ScopeIR(
        kind="quantifier",
        variables={"x0": "symbolic"},
        neighborhood=None,
        domain=DomainIR(
            entries=(
                DomainEntryIR(
                    entity="x0",
                    feature="Segment",
                    constraint=FiniteSetDomainIR(
                        values=(
                            SymbolLiteralIR("A"),
                            SymbolLiteralIR("B"),
                        )
                    ),
                ),
            )
        ),
    )

    got = normalizer().normalize_task(task)

    assert_quantifier_scope(got)
    assert_scope_domain_values(got, "Segment", ["A", "B"])
    assert sexpr(got.query.expression) == (
        "OR(NOT(CMP(x0.a <= 1)), NOT(CMP(x0.b <= 2)))"
    )
    assert_is_nnf(got.query.expression)
