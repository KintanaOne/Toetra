from __future__ import annotations

from toetra._compiler.parser.parser import parse_toetra_code
from tests.support.parser_points import (
    program,
    single_tree,
)

# ---------------------------------------------------------------------------
# PAR-WHERE-*, PAR-NBH-*, PAR-CHK-*, PAR-AT-*, and PAR-PAIR-*
# ---------------------------------------------------------------------------


def test_par_where_001_simple_restriction_parses() -> None:
    tree = parse_toetra_code(
        program(body="forall x0, x1 where x1.age >= x0.age => target[x1] >= target[x0]")
    )

    restriction = single_tree(tree, "restriction")
    assert len(list(restriction.find_data("comparison_expr"))) == 1


def test_par_where_002_parenthesized_compound_restriction_parses() -> None:
    tree = parse_toetra_code(program(body="""
            forall x0, x1
            where (
                x1.income >= x0.income
                and x1.age == x0.age
            )
            => target[x1] <= target[x0]
            """))

    restriction = single_tree(tree, "restriction")
    assert len(list(restriction.find_data("logic_and"))) == 1
    assert len(list(restriction.find_data("comparison_expr"))) == 2
