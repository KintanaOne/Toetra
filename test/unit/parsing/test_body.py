import pytest
from lark import Tree

from forml.parser.parser import parse_forml_code
from forml.ast.queries import (
    get_property_expression,
    get_assertion_expression,
    get_abstractor
)
from test.fixtures.program_samples import (
    INVALID_BODY_EMPTY,
    INVALID_BODY_INVALID_ASSERTION,
    INVALID_BODY_SYNTAX_ERROR,
    VALID_PROGRAM_WITH_ABSTRACTOR,
    VALID_PROGRAM_WITH_BODY_SIMPLE_ASSERTION
)

def parse(code: str) -> Tree:
    return parse_forml_code(code)

def test_body_simple_assertion():

    tree = parse(VALID_PROGRAM_WITH_BODY_SIMPLE_ASSERTION)

    property = get_property_expression(tree)

    assertion = get_assertion_expression(tree)

    assert property is not None

    assert assertion is not None

def test_body_with_abstractor():

    tree = parse(VALID_PROGRAM_WITH_ABSTRACTOR)

    prop = get_property_expression(tree)

    # abstraction layer exists 
    abstractor = get_abstractor(tree)

    assert abstractor is not None

def test_body_empty():

    with pytest.raises(Exception):
        parse(INVALID_BODY_EMPTY)

def test_body_syntax_error():

    with pytest.raises(Exception):
        parse(INVALID_BODY_SYNTAX_ERROR)

def test_body_invalid_assertion():

    with pytest.raises(Exception):
        parse(INVALID_BODY_INVALID_ASSERTION)

