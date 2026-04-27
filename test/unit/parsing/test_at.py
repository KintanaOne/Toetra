from typing import cast

import pytest
from lark import Tree

from dsl.ast.nodes.expressions import AtExprNode
from dsl.builder import neighborhood
from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code

from test.fixtures.properties_samples import *


def parse(code: str) -> Tree:
    return parse_forml_code(code)


# ----------------------------------------------------------------------------------------------------------------------
# VALID
# ----------------------------------------------------------------------------------------------------------------------

def test_at_basic():
    prop = parse_program(parse(VALID_MINIMAL_AT)).body[0]

    scope = prop.rule.scope
    assert isinstance(scope, AtExprNode)
    scope = cast(AtExprNode, scope)
    
    assert prop.type == "ROBUSTNESS"
    assert scope.variable == "x0"
    assert scope.neighborhood is None
    assert scope.domain is None
    assert prop.rule.assertion is not None
    assert prop.backend is None


def test_at_with_neighborhood():
    prop = parse_program(parse(VALID_AT_WITH_NEIGHBORHOOD)).body[0]

    scope = prop.rule.scope
    assert isinstance(scope, AtExprNode)
    scope = cast(AtExprNode, scope)

    neigh = scope.neighborhood
    
    assert neigh is not None
    assert neigh.metric == "L2"
    assert neigh.args[0].key == "eps"
    assert neigh.args[0].value == 0.01
    assert scope.domain is None


def test_at_with_domain():
    prop = parse_program(parse(VALID_AT_WITH_DOMAIN)).body[0]

    scope = prop.rule.scope
    assert isinstance(scope, AtExprNode)
    scope = cast(AtExprNode, scope)

    domain = scope.domain


    assert domain is not None
    assert domain.name == "sex"
    assert domain.values == ["male", "female"]


def test_at_with_neighborhood_and_domain():
    prop = parse_program(parse(VALID_AT_WITH_NEIGHBORHOOD_AND_DOMAIN)).body[0]

    scope = prop.rule.scope
    assert isinstance(scope, AtExprNode)
    scope = cast(AtExprNode, scope)

    neighborhood = scope.neighborhood
    domain = scope.domain

    assert neighborhood is not None
    assert neighborhood.metric is not None
    assert neighborhood.args is not None
    assert neighborhood.metric == "L2"

    assert domain is not None
    assert domain.name is not None
    assert domain.name == "sex"


# ----------------------------------------------------------------------------------------------------------------------
# INVALID
# ----------------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("code", [
    INVALID_AT_MISSING_IDENTIFIER,
    INVALID_AT_INVALID_NEIGHBORHOOD_ARGUMENTS,
    INVALID_AT_INVALID_NEIGHBORHOOD_SYNTAX,
    INVALID_AT_INVALID_DOMAIN_VALUES,
    INVALID_AT_INVALID_DOMAIN_SYNTAX,
])
def test_at_invalid(code):
    with pytest.raises(Exception):
        parse(code)