from __future__ import annotations

from dsl.parser.parser import parse_forml_code
from test.unit.parser._point_binding_helpers import (
    program,
    single_tree,
)

# ---------------------------------------------------------------------------
# PAR-WHERE-*, PAR-NBH-*, PAR-CHK-*, PAR-AT-*, and PAR-PAIR-*
# ---------------------------------------------------------------------------


def test_par_where_001_simple_restriction_parses() -> None:
    tree = parse_forml_code(
        program(body="forall x0, x1 where x1.age >= x0.age => target[x1] >= target[x0]")
    )

    restriction = single_tree(tree, "restriction")
    assert len(list(restriction.find_data("comparison_expr"))) == 1


def test_par_where_002_parenthesized_compound_restriction_parses() -> None:
    tree = parse_forml_code(program(body="""
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
