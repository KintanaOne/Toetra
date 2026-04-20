from pathlib import Path

import pytest
from lark import Tree

from dsl.builder.expressions import parse_at
from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code

from test.fixtures.properties_samples import (
    INVALID_AT_INVALID_DOMAIN_VALUES,
    INVALID_AT_INVALID_NEIGHBORHOOD_ARGUMENTS,
    INVALID_AT_MISSING_IDENTIFIER,
    INVALID_AT_INVALID_DOMAIN_SYNTAX,
    INVALID_AT_INVALID_NEIGHBORHOOD_SYNTAX,
    VALID_AT_WITH_DOMAIN,
    VALID_AT_WITH_NEIGHBORHOOD,
    VALID_AT_WITH_NEIGHBORHOOD_AND_DOMAIN,
    VALID_MINIMAL_AT,
)

def parse(code: str) -> Tree:
    return parse_forml_code(code)


#----------------------------------------------------------------------------------------------------------------------#
#                                             VALID CASES
#----------------------------------------------------------------------------------------------------------------------#

def test_at_basic():
    """ AT1 : Test parsing of a basic at expression."""

    tree = parse(VALID_MINIMAL_AT)
    program = parse_program(tree)
    property = program["properties"][0]

    expr = property["expr"]
    neighborhood = expr["neighborhood"]
    domain = expr["domain"]
    assertion = property["assertion"]
    abstractor = property["abstractor"]
    
    assert property["type"] == "ROBUSTNESS"
    assert expr["kind"] == "at"
    assert expr["variable"] == "x0"
    assert neighborhood == None
    assert domain == None
    assert assertion is not None
    assert abstractor is None

def test_at_with_neighborhood():
    """ AT2 : Test parsing of an at expression with a neighborhood."""

    tree = parse(VALID_AT_WITH_NEIGHBORHOOD)
    program = parse_program(tree)
    property = program["properties"][0]

    expr = property["expr"]
    neighborhood = expr["neighborhood"]
    domain = expr["domain"]
    assertion = property["assertion"]
    abstractor = property["abstractor"]
    
    assert property["type"] == "ROBUSTNESS"
    assert expr["kind"] == "at"
    assert expr["variable"] == "x0"
    assert neighborhood["metric"] == "L2"
    assert neighborhood["args"]["eps"] == 0.01
    assert domain == None
    assert assertion is not None
    assert abstractor is None


def test_at_with_domain():
    """ AT3 : Test parsing of an at expression with a domain."""

    tree = parse(VALID_AT_WITH_DOMAIN)
    program = parse_program(tree)
    property = program["properties"][0]

    expr = property["expr"]
    neighborhood = expr["neighborhood"]
    domain = expr["domain"]
    assertion = property["assertion"]
    abstractor = property["abstractor"]
    
    assert property["type"] == "ROBUSTNESS"
    assert expr["kind"] == "at"
    assert expr["variable"] == "x0"
    assert neighborhood == None
    assert domain["name"] == "sex"
    assert domain["values"] == ["male", "female"]
    assert assertion is not None
    assert abstractor is None


def test_at_with_neighborhood_and_domain():
    """ AT4 : Test parsing of an at expression with a neighborhood and domain."""

    tree = parse(VALID_AT_WITH_NEIGHBORHOOD_AND_DOMAIN)
    program = parse_program(tree)
    property = program["properties"][0]

    expr = property["expr"]
    neighborhood = expr["neighborhood"]
    domain = expr["domain"]
    assertion = property["assertion"]
    abstractor = property["abstractor"]
    
    assert property["type"] == "ROBUSTNESS"
    assert expr["kind"] == "at"
    assert expr["variable"] == "x0"
    assert neighborhood["metric"] == "L2"
    assert neighborhood["args"]["eps"] == 0.01
    assert domain["name"] == "sex"
    assert domain["values"] == ["male", "female"]
    assert assertion is not None
    assert abstractor is None

#----------------------------------------------------------------------------------------------------------------------#
#                                             INVALID CASES
#----------------------------------------------------------------------------------------------------------------------#

def test_at_missing_identifier():
    """AT5 — missing identifier"""

    with pytest.raises(Exception):
        parse(INVALID_AT_MISSING_IDENTIFIER)


def test_at_invalid_neighborhood_arguments():
    """AT6 — malformed neighborhood"""

    with pytest.raises(Exception):
        parse(INVALID_AT_INVALID_NEIGHBORHOOD_ARGUMENTS)


def test_at_invalid_neighborhood_syntax():

    with pytest.raises(Exception):
        parse(INVALID_AT_INVALID_NEIGHBORHOOD_SYNTAX)


def test_at_invalid_domain_values():
    """AT8 — invalid domain values"""

    with pytest.raises(Exception):
        parse(INVALID_AT_INVALID_DOMAIN_VALUES)


def test_at_invalid_domain_syntax():
    """AT9 — invalid domain syntax"""

    with pytest.raises(Exception):
        parse(INVALID_AT_INVALID_DOMAIN_SYNTAX)