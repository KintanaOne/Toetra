from pathlib import Path

import pytest
from lark import Tree

from forml.ast.queries import (
    get_check_at_expression,
    get_assertion_expression,
    get_identifiers,
    get_identifier_value,
)
from forml.parser.parser import parse_forml_code
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

    check_at_expr = get_check_at_expression(tree)
    identifiers = get_identifiers(check_at_expr)
    assertion = get_assertion_expression(tree)

    assert check_at_expr is not None
    assert len(identifiers) == 1
    assert get_identifier_value(identifiers[0]) == "x0"
    assert assertion is not None


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

    check_at_expr = get_check_at_expression(tree)
    assertion = get_assertion_expression(tree)

    assert check_at_expr is not None
    assert assertion is not None

    # Bonus robuste : vérifier qu'on retrouve bien x0 dans l'expression logique
    identifiers = get_identifiers(assertion)
    values = [get_identifier_value(i) for i in identifiers]

    assert "x0" in values