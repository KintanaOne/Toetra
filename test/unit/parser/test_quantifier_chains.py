from __future__ import annotations

import pytest
from lark.exceptions import UnexpectedInput
from dsl.parser.parser import parse_toetra_code
from test.unit.parser._point_binding_helpers import (
    direct_trees,
    program,
    single_tree,
    token_text,
    walk_preorder,
)

# ---------------------------------------------------------------------------
# PAR-QP-* — binder lists, ordered chains, domain, and restriction placement
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("clause", "expected_quantifier"),
    [
        pytest.param("forall x0, x1", "forall", id="PAR-QP-001-forall-list"),
        pytest.param("exists x0, x1", "exists", id="PAR-QP-002-exists-list"),
    ],
)
def test_quantifier_list_order_is_preserved(
    clause: str,
    expected_quantifier: str,
) -> None:
    tree = parse_toetra_code(program(body=f"{clause} => target[x0] <= 7"))
    expression = single_tree(tree, "quantifier_expr")

    quantifier = direct_trees(expression, "quantifier")
    identifiers = direct_trees(expression, "identifier")

    assert len(quantifier) == 1
    assert token_text(quantifier[0]) == expected_quantifier
    assert [token_text(identifier) for identifier in identifiers] == ["x0", "x1"]


def test_par_qp_003_mixed_quantifier_chain_order_is_preserved() -> None:
    tree = parse_toetra_code(
        program(body="forall x0 exists x1 => target[x1] >= target[x0]")
    )
    expression = single_tree(tree, "quantifier_expr")

    quantifiers = [
        token_text(node)
        for node in walk_preorder(expression)
        if node.data == "quantifier"
    ]
    identifiers = [
        token_text(node)
        for node in walk_preorder(expression)
        if node.data == "identifier"
    ]

    assert quantifiers == ["forall", "exists"]
    assert identifiers[:2] == ["x0", "x1"]


def test_par_qp_004_indentation_does_not_change_cst_structure() -> None:
    flat = parse_toetra_code(
        program(body="forall x0 exists x1 => target[x1] >= target[x0]")
    )
    indented = parse_toetra_code(program(body="""
            forall x0
                exists x1
                    => target[x1] >= target[x0]
            """))

    assert flat == indented


@pytest.mark.parametrize(
    "body",
    [
        pytest.param(
            "forall x0, => target[x0] <= 7",
            id="PAR-QP-005-trailing-comma",
        ),
        pytest.param(
            "forall x0, exists x1 => target[x0] <= 7",
            id="PAR-QP-007-missing-name-after-comma",
        ),
    ],
)
def test_invalid_quantifier_list_surface_is_rejected(body: str) -> None:
    with pytest.raises(UnexpectedInput):
        parse_toetra_code(program(body=body))


def test_par_qp_006_duplicate_name_parses_for_semantic_rejection() -> None:
    tree = parse_toetra_code(program(body="forall x0, x0 => target[x0] <= 7"))
    expression = single_tree(tree, "quantifier_expr")
    assert [
        token_text(identifier) for identifier in direct_trees(expression, "identifier")
    ] == ["x0", "x0"]


def test_par_qp_008_domain_after_full_chain_parses() -> None:
    tree = parse_toetra_code(program(body="""
            forall x0
            exists x1
            with domain(
                x0.age: [18, 90],
                x1.age: [18, 90]
            )
            => target[x1] >= target[x0]
            """))

    expression = single_tree(tree, "quantifier_expr")
    assert len(list(expression.find_data("quantifier"))) == 2
    assert len(list(expression.find_data("domain_entry"))) == 2


def test_par_qp_009_where_after_domain_parses() -> None:
    tree = parse_toetra_code(program(body="""
            forall x0, x1
            with domain(
                x0.age: [18, 90],
                x1.age: [18, 90]
            )
            where x1.age >= x0.age
            => target[x1] >= target[x0]
            """))

    expression = single_tree(tree, "quantifier_expr")
    assert len(list(expression.find_data("domain"))) == 1
    assert len(list(expression.find_data("where_clause"))) == 1


def test_par_qp_010_where_before_domain_is_rejected() -> None:
    with pytest.raises(UnexpectedInput):
        parse_toetra_code(program(body="""
                forall x0, x1
                where x1.age >= x0.age
                with domain(x0.age: [18, 90])
                => target[x1] >= target[x0]
                """))
