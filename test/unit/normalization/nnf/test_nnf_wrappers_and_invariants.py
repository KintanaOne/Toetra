from __future__ import annotations

from dsl.ir.ir1.nodes import AndIR, ImplyIR, NotIR, OrIR, QueryIR

from test.fixtures.normalization.nnf.helpers import assert_is_nnf, cmp, normalizer, sexpr, task_with_expr



def test_normalize_query_normalizes_query_expression():
    query = QueryIR(
        expression=NotIR(
            AndIR(
                operands=[
                    cmp("a", 1),
                    cmp("b", 2),
                ]
            )
        )
    )

    got = normalizer().normalize_query(query)

    assert sexpr(got.expression) == "OR(NOT(CMP(x0.a <= 1)), NOT(CMP(x0.b <= 2)))"
    assert_is_nnf(got.expression)



def test_normalize_task_preserves_non_query_metadata():
    expr = ImplyIR(left=cmp("a", 1), right=cmp("b", 2))
    task = task_with_expr(expr)

    got = normalizer().normalize_task(task)

    assert got.property_type == task.property_type
    assert got.scope == task.scope
    assert got.backend == task.backend
    assert sexpr(got.query.expression) == "OR(NOT(CMP(x0.a <= 1)), CMP(x0.b <= 2))"
    assert_is_nnf(got.query.expression)



def test_normalize_tasks_normalizes_all_tasks():
    tasks = [
        task_with_expr(ImplyIR(left=cmp("a", 1), right=cmp("b", 2))),
        task_with_expr(NotIR(OrIR(operands=[cmp("c", 3), cmp("d", 4)]))),
    ]

    got = normalizer().normalize_tasks(tasks)

    assert len(got) == 2
    assert sexpr(got[0].query.expression) == "OR(NOT(CMP(x0.a <= 1)), CMP(x0.b <= 2))"
    assert sexpr(got[1].query.expression) == "AND(NOT(CMP(x0.c <= 3)), NOT(CMP(x0.d <= 4)))"

    for task in got:
        assert_is_nnf(task.query.expression)



def test_normalization_is_idempotent():
    expr = NotIR(
        OrIR(
            operands=[
                ImplyIR(left=cmp("a", 1), right=cmp("b", 2)),
                NotIR(cmp("c", 3)),
            ]
        )
    )

    first = normalizer().normalize_expr(expr)
    second = normalizer().normalize_expr(first)

    assert sexpr(second) == sexpr(first)
    assert_is_nnf(second)
