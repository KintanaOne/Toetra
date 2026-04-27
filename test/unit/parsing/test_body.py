from typing import cast

import pytest
from lark import Tree

from dsl.ast.nodes.expressions import PairwiseExprNode
from dsl.builder.expressions import parse_pairwise
from dsl.builder.program import parse_program
from dsl.builder.property import parse_property
from dsl.parser.parser import parse_forml_code
from test.fixtures.program_samples import (
    INVALID_BODY_EMPTY,
    INVALID_BODY_INVALID_ASSERTION,
    INVALID_BODY_SYNTAX_ERROR,
    VALID_PROGRAM_WITH_BACKEND,
    VALID_PROGRAM_WITH_BODY_SIMPLE_ASSERTION
)

def parse(code: str) -> Tree:
    return parse_forml_code(code)

def test_body_simple_assertion():

    prop = parse_program(parse(VALID_PROGRAM_WITH_BODY_SIMPLE_ASSERTION)).body[0]

    scope = prop.rule.scope
    assert isinstance(scope, PairwiseExprNode)
    scope = cast(PairwiseExprNode, scope)

    neigh = scope.neighborhood
    
    assert neigh is not None
    assert neigh.metric == "L2"
    assert neigh.args[0].key == "eps"
    assert neigh.args[0].value == 0.01
    assert scope.domain is None

def test_body_with_abstractor():

    prop = parse_program(parse(VALID_PROGRAM_WITH_BACKEND)).body[0]

    scope = prop.rule.scope
    assert isinstance(scope, PairwiseExprNode)
    scope = cast(PairwiseExprNode, scope)

    # backend layer exists 
    backend = prop.backend

    assert backend is not None
    assert backend.name
    assert backend.args[0].key == "param1"
    assert backend.args[0].value == "a"


def test_body_empty():

    with pytest.raises(Exception):
        parse(INVALID_BODY_EMPTY)

def test_body_syntax_error():

    with pytest.raises(Exception):
        parse(INVALID_BODY_SYNTAX_ERROR)

def test_body_invalid_assertion():

    with pytest.raises(Exception):
        parse(INVALID_BODY_INVALID_ASSERTION)

