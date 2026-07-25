from __future__ import annotations

import pytest
from lark.exceptions import UnexpectedInput
from lark import Token
from dsl.parser.parser import parse_toetra_code
from test.unit.parser._point_binding_helpers import (
    direct_trees,
    program,
    single_tree,
    token_text,
)


def test_par_nbh_001_natural_membership_preserves_all_arguments() -> None:
    tree = parse_toetra_code(
        program(
            declarations="anchor x0 := { age: 42 }",
            body="""
            forall x1
            where x1 in neighborhood(
                of = x0,
                metric = Linf,
                eps = 0.05
            )
            => target[x1] >= target[x0]
            """,
        )
    )

    membership = single_tree(tree, "neighborhood_membership")
    candidate = direct_trees(membership, "identifier")
    anchor_argument = single_tree(membership, "neighborhood_of_argument")
    metric_argument = single_tree(membership, "neighborhood_metric_argument")
    eps_argument = single_tree(membership, "neighborhood_eps_argument")

    assert [token_text(identifier) for identifier in candidate] == ["x1"]
    assert token_text(single_tree(anchor_argument, "identifier")) == "x0"
    assert [
        str(token)
        for token in metric_argument.scan_values(
            lambda value: isinstance(value, Token)
            and value.type in {"L1", "L2", "LINF"}
        )
    ] == ["Linf"]
    assert token_text(single_tree(eps_argument, "scalar_expression")) == "0.05"


@pytest.mark.parametrize(
    "restriction",
    [
        pytest.param(
            "in neighborhood(of = x0, metric = Linf, eps = 0.05)",
            id="PAR-NBH-002-missing-candidate",
        ),
        pytest.param(
            "x1 in neighborhood(metric = Linf, eps = 0.05)",
            id="PAR-NBH-003-missing-of",
        ),
        pytest.param(
            "x1 in neighborhood(of = x0, eps = 0.05)",
            id="PAR-NBH-004-missing-metric",
        ),
        pytest.param(
            "x1 in neighborhood(of = x0, metric = Linf)",
            id="PAR-NBH-005-missing-eps",
        ),
    ],
)
def test_invalid_natural_neighborhood_surface_is_rejected(
    restriction: str,
) -> None:
    with pytest.raises(UnexpectedInput):
        parse_toetra_code(
            program(
                declarations="anchor x0 := { age: 42 }",
                body=f"forall x1 where {restriction} => target[x1] >= target[x0]",
            )
        )
