from typing import cast

import pytest
from lark import Tree

from dsl.ast.nodes.expressions import PairwiseExprNode
from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code
from test.fixtures.properties_samples import (
    INVALID_PAIRWISE_MALFORMED_ABSTRACTOR,
    INVALID_PAIRWISE_MALFORMED_NEIGHBORHOOD,
    INVALID_PAIRWISE_MISSING_ASSERTION,
    INVALID_PAIRWISE_MISSING_BOTH_IDENTIFIERS,
    INVALID_PAIRWISE_MISSING_IDENTIFIER,
    INVALID_PAIRWISE_MISSING_IDENTIFIER_PRIME,
    INVALID_PAIRWISE_MISSING_NEIGHBORHOOD_SYNTAX,
    VALID_PAIRWISE_WITH_ABSTRACTOR,
    VALID_MINIMAL_PAIRWISE,
)


def parse(code: str) -> Tree:
    return parse_forml_code(code)


# ----------------------------------------------------------------------------------------------------------------------
# VALID
# ----------------------------------------------------------------------------------------------------------------------

def test_pairwise_basic():

    prop = parse_program(parse(VALID_MINIMAL_PAIRWISE)).body[0]

    scope = prop.rule.scope
    assert isinstance(scope, PairwiseExprNode)
    scope = cast(PairwiseExprNode, scope)

    pair = scope.pair
    
    parts = pair.split("~")
    if len(parts) != 2:
        raise ValueError(f"Invalid pair format: {pair}")

    left, right = [x.strip() for x in parts]

    neigh = scope.neighborhood
    domain = scope.domain
    backend = prop.backend

    assert prop.type == "ROBUSTNESS"

    assert left == "x"
    assert right == "x'"

    assert neigh.metric == "L2"
    assert neigh.args[0].key == "eps"
    assert neigh.args[0].value == 0.01

    assert domain is None

    assert backend is None


def test_pairwise_with_backend():

    prop = parse_program(parse(VALID_PAIRWISE_WITH_ABSTRACTOR)).body[0]

    scope = prop.rule.scope
    assert isinstance(scope, PairwiseExprNode)
    scope = cast(PairwiseExprNode, scope)

    pair = scope.pair
    
    parts = pair.split("~")
    if len(parts) != 2:
        raise ValueError(f"Invalid pair format: {pair}")

    left, right = [x.strip() for x in parts]

    neigh = scope.neighborhood
    domain = scope.domain
    backend = prop.backend

    assert prop.type == "ROBUSTNESS"

    assert left == "x"
    assert right == "x'"

    assert neigh.metric == "L2"
    assert neigh.args[0].key == "eps"
    assert neigh.args[0].value == 0.01

    assert domain is None

    assert backend is not None
    assert backend.name == "Z3"

# ----------------------------------------------------------------------------------------------------------------------
# INVALID
# ----------------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("code", [
    INVALID_PAIRWISE_MALFORMED_ABSTRACTOR,
    INVALID_PAIRWISE_MISSING_NEIGHBORHOOD_SYNTAX,
    INVALID_PAIRWISE_MALFORMED_NEIGHBORHOOD,
    INVALID_PAIRWISE_MISSING_ASSERTION,
    INVALID_PAIRWISE_MISSING_IDENTIFIER,
    INVALID_PAIRWISE_MISSING_IDENTIFIER_PRIME,
    INVALID_PAIRWISE_MISSING_BOTH_IDENTIFIERS,
])
def test_pairwise_invalid(code):
    with pytest.raises(Exception):
        parse(code)