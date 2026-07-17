from __future__ import annotations

from lark import Token
from dsl.parser.parser import parse_forml_code
from test.unit.parser._point_binding_helpers import (
    direct_trees,
    program,
    single_tree,
    token_text,
)


def test_par_chk_001_check_at_selection_sugar_parses() -> None:
    tree = parse_forml_code(
        program(
            declarations="anchor x0 := { age: 42 }",
            body="check_at x0 => target <= 7",
        )
    )

    check = single_tree(tree, "check_expr")
    assert token_text(single_tree(check, "identifier")) == "x0"


def test_par_at_001_local_sugar_preserves_anchor_candidate_and_arguments() -> None:
    tree = parse_forml_code(
        program(
            declarations="anchor x0 := { age: 42 }",
            body="""
            at x0 with x1 in neighborhood(
                metric = Linf,
                eps = 0.05
            )
            => target[x1] >= target[x0]
            """,
        )
    )

    at_expr = single_tree(tree, "at_expr")
    local = single_tree(at_expr, "local_neighborhood")

    assert token_text(direct_trees(at_expr, "identifier")[0]) == "x0"
    assert token_text(direct_trees(local, "identifier")[0]) == "x1"
    assert [
        str(token)
        for token in single_tree(local, "neighborhood_metric_argument").scan_values(
            lambda value: isinstance(value, Token)
            and value.type in {"L1", "L2", "LINF"}
        )
    ] == ["Linf"]
    assert token_text(single_tree(local, "scalar_expression")) == "0.05"


def test_par_at_002_legacy_at_has_explicit_legacy_cst_branch() -> None:
    tree = parse_forml_code(
        program(body="at x0 in neighborhood(L2, eps=0.01) => x0.age <= 7")
    )

    at_expr = single_tree(tree, "at_expr")
    assert len(list(at_expr.find_data("legacy_at_suffix"))) == 1
    assert not list(at_expr.find_data("local_neighborhood"))


def test_par_pair_001_legacy_pairwise_has_explicit_cst_branch() -> None:
    tree = parse_forml_code(
        program(body="x ~ x' in neighborhood(L2, eps=0.01) => x.age <= 7")
    )

    assert len(list(tree.find_data("pairwise_expr"))) == 1
    assert len(list(tree.find_data("pairwise_token"))) == 1
