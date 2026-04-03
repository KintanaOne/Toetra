from pathlib import Path

import pytest
from lark import Tree

from forml.ast.queries import (
    get_at_expression,
    get_domain_dict,
    get_neighborhood_dict,
    get_identifier_value,
    get_identifiers,
)
from forml.parser.parser import parse_forml_code

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

    at_expr = get_at_expression(tree)
    identifiers = get_identifiers(at_expr)

    assert at_expr is not None
    assert len(identifiers) == 1
    assert get_identifier_value(identifiers[0]) == "x0"


def test_at_with_neighborhood():
    """ AT2 : Test parsing of an at expression with a neighborhood."""

    tree = parse(VALID_AT_WITH_NEIGHBORHOOD)

    at_expr = get_at_expression(tree)
    neighborhood = get_neighborhood_dict(at_expr)

    assert at_expr is not None
    assert neighborhood is not None
    assert neighborhood["metric"] == "L2"
    assert neighborhood["args"]["eps"] == "0.01"


def test_at_with_domain():
    """ AT3 : Test parsing of an at expression with a domain."""

    tree = parse(VALID_AT_WITH_DOMAIN)

    at_expr = get_at_expression(tree)
    domain = get_domain_dict(at_expr)

    assert at_expr is not None
    assert domain is not None
    assert domain["name"] == "sex"
    assert domain["values"] == ["male", "female"]


def test_at_with_neighborhood_and_domain():
    """ AT4 : Test parsing of an at expression with a neighborhood and domain."""

    tree = parse(VALID_AT_WITH_NEIGHBORHOOD_AND_DOMAIN)

    at_expr = get_at_expression(tree)
    neighborhood = get_neighborhood_dict(at_expr)
    domain = get_domain_dict(at_expr)

    assert at_expr is not None
    assert neighborhood is not None
    assert domain is not None


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