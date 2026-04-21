import pytest
from lark import Tree

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

    tree = parse(VALID_PROGRAM_WITH_BODY_SIMPLE_ASSERTION)

    program = parse_program(tree)
    property = program.body[0]

    left = property.implication.left
    right = property.implication.right

    assert len(program.body) == 1

    assert right is not None


def test_body_with_abstractor():

    tree = parse(VALID_PROGRAM_WITH_BACKEND)

    program = parse_program(tree)
    property = program.body[0]

    # backend layer exists 
    backend = property.backend

    assert backend.name == "eran"
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

