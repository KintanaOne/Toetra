from pathlib import Path

import pytest
from lark import Tree

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
    VALID_MINIMAL_PAIRWISE 
)

def parse(code: str) -> Tree:
    return parse_forml_code(code)


#----------------------------------------------------------------------------------------------------------------------#
#                                             VALID CASES
#----------------------------------------------------------------------------------------------------------------------#

def test_pairwise_basic():
    """ PW1 : Basic pairwise expression """

    tree = parse(VALID_MINIMAL_PAIRWISE)
    program = parse_program(tree)
    property = program["properties"][0]

    expr = property["expr"]
    neighborhood = expr["neighborhood"]
    domain = expr["domain"]
    assertion = property["assertion"]
    abstractor = property["abstractor"]
    
    assert property["type"] == "ROBUSTNESS"
    assert expr["kind"] == "pairwise"
    assert expr["pair"] == "x ~ x'"
    assert neighborhood["metric"] == "L2"
    assert neighborhood["args"]["eps"] == 0.01
    assert domain == None
    assert assertion is not None
    assert abstractor is None


def test_pairwise_with_using():
    """ PW2 : Pairwise with abstractor """

    tree = parse(VALID_PAIRWISE_WITH_ABSTRACTOR)
    program = parse_program(tree)
    property = program["properties"][0]

    expr = property["expr"]
    neighborhood = expr["neighborhood"]
    domain = expr["domain"]
    assertion = property["assertion"]
    abstractor = property["abstractor"]
    
    assert property["type"] == "ROBUSTNESS"
    assert expr["kind"] == "pairwise"
    assert expr["pair"] == "x ~ x'"
    assert neighborhood["metric"] == "L2"
    assert neighborhood["args"]["eps"] == 0.01
    assert domain == None
    assert assertion is not None
    assert abstractor["name"] == "Z3"


#----------------------------------------------------------------------------------------------------------------------#
#                                             INVALID CASES
#----------------------------------------------------------------------------------------------------------------------#

def test_pairwise_malformed_abstractor():
    """ PW3 : Missing 'using' keyword """

    with pytest.raises(Exception):
        parse(INVALID_PAIRWISE_MALFORMED_ABSTRACTOR)


def test_pairwise_missing_neighborhood_syntax():
    """ PW4 : Missing neighborhood """

    with pytest.raises(Exception):
        parse(INVALID_PAIRWISE_MISSING_NEIGHBORHOOD_SYNTAX)


def test_pairwise_malformed_neighborhood():
    """ PW5 : Malformed neighborhood """

    with pytest.raises(Exception):
        parse(INVALID_PAIRWISE_MALFORMED_NEIGHBORHOOD)


def test_pairwise_missing_assertion():
    """ PW6 : Missing assertion """

    with pytest.raises(Exception):
        parse(INVALID_PAIRWISE_MISSING_ASSERTION)


def test_pairwise_missing_identifier():
    """ PW7 : Missing identifier """

    with pytest.raises(Exception):
        parse(INVALID_PAIRWISE_MISSING_IDENTIFIER)


def test_pairwise_missing_identifier_prime():
    """ PW8 : Missing identifier prime """

    with pytest.raises(Exception):
        parse(INVALID_PAIRWISE_MISSING_IDENTIFIER_PRIME)


def test_pairwise_missing_both_identifiers():
    """ PW9 : Missing both identifiers """

    with pytest.raises(Exception):
        parse(INVALID_PAIRWISE_MISSING_BOTH_IDENTIFIERS)
