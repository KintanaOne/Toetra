from pathlib import Path

import pytest
from lark import Tree

from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code
from test.fixtures.properties_samples import (
    INVALID_CHECK_AT_INVALID_IDENTIFIER,
    INVALID_CHECK_AT_MISSING_ASSERTION,
    INVALID_CHECK_AT_MISSING_IDENTIFIER,
    VALID_CHECK_AT_WITH_COMPLEX_ASSERTION,
    VALID_MINIMAL_CHECK_AT
)

def parse(code: str) -> Tree:
    return parse_forml_code(code)


#----------------------------------------------------------------------------------------------------------------------#
#                                             VALID CASES
#----------------------------------------------------------------------------------------------------------------------#

def test_check_at_basic():
    """ C1 : Test parsing of a basic check_at expression."""

    tree = parse(VALID_MINIMAL_CHECK_AT)
    program = parse_program(tree)
    property = program.body[0]

    left = property.implication.left
    right = property.implication.right

    assert left is not None
    assert right is not None


#----------------------------------------------------------------------------------------------------------------------#
#                                             INVALID CASES
#----------------------------------------------------------------------------------------------------------------------#

def test_check_at_missing_identifier():
    """ C2 : Missing identifier """

    with pytest.raises(Exception):
        parse(INVALID_CHECK_AT_MISSING_IDENTIFIER)


def test_check_at_missing_assertion():
    """ C3 : Missing assertion """

    with pytest.raises(Exception):
        parse(INVALID_CHECK_AT_MISSING_ASSERTION)


def test_check_at_with_invalid_identifier():
    """ C4 : Invalid identifier """

    with pytest.raises(Exception):
        parse(INVALID_CHECK_AT_INVALID_IDENTIFIER)


#----------------------------------------------------------------------------------------------------------------------#
#                                             EDGE CASES
#----------------------------------------------------------------------------------------------------------------------#

def test_check_at_with_complex_assertion():
    """ C5 : Complex logical assertion """

    tree = parse(VALID_CHECK_AT_WITH_COMPLEX_ASSERTION)

    program = parse_program(tree)
    property = program.body[0]

    left = property.implication.left
    right = property.implication.right
    
    

    assert left is not None
    assert right is not None