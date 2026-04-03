import pytest
from lark import Tree

from forml.parser.parser import parse_forml_code
from forml.ast.queries import (
    get_all_properties,
    get_property_dict,
)
from test.fixtures.program_samples import INVALID_BODY_MISSING_EXPRESSION, INVALID_BODY_MISSING_EXPRESSION, INVALID_BODY_MULTIPLE_EXPRESSION
from test.fixtures.properties_samples import (
    VALID_AT_WITH_NEIGHBORHOOD,
    VALID_MINIMAL_CHECK_AT,
    VALID_FORALL_WITH_DOMAIN,
    VALID_MINIMAL_PAIRWISE
)


def parse(code: str) -> Tree:
    return parse_forml_code(code)


#----------------------------------------------------------------------------------------------------------------------#
#                                             FORALL
#----------------------------------------------------------------------------------------------------------------------#

def test_property_with_quantifier():

    tree = parse(VALID_FORALL_WITH_DOMAIN)

    prop = get_all_properties(tree)[0]
    data = get_property_dict(prop)

    assert data["mode"] == "quantifier"
    assert data["quantifier"] == "forall"
    assert data["domain"]["name"] == "gender"
    assert data["domain"]["values"] == ["male", "female"]


#----------------------------------------------------------------------------------------------------------------------#
#                                             AT
#----------------------------------------------------------------------------------------------------------------------#

def test_property_with_at():

    tree = parse(VALID_AT_WITH_NEIGHBORHOOD)

    prop = get_all_properties(tree)[0]
    data = get_property_dict(prop)

    assert data["mode"] == "at"
    assert data["neighborhood"]["metric"] == "L2"
    assert data["neighborhood"]["args"]["eps"] == "0.01"


#----------------------------------------------------------------------------------------------------------------------#
#                                             CHECK_AT
#----------------------------------------------------------------------------------------------------------------------#

def test_property_with_check_at():

    tree = parse(VALID_MINIMAL_CHECK_AT)

    prop = get_all_properties(tree)[0]
    data = get_property_dict(prop)

    assert data["mode"] == "check_at"


#----------------------------------------------------------------------------------------------------------------------#
#                                             PAIRWISE
#----------------------------------------------------------------------------------------------------------------------#

def test_property_with_pairwise():

    tree = parse(VALID_MINIMAL_PAIRWISE)

    prop = get_all_properties(tree)[0]
    data = get_property_dict(prop)

    assert data["mode"] == "pairwise"
    assert data["neighborhood"]["metric"] == "L2"


#----------------------------------------------------------------------------------------------------------------------#
#                                             DOMAIN
#----------------------------------------------------------------------------------------------------------------------#

def test_property_with_domain():

    tree = parse(VALID_FORALL_WITH_DOMAIN)

    prop = get_all_properties(tree)[0]
    data = get_property_dict(prop)

    assert data["domain"]["name"] == "gender"
    assert data["domain"]["values"] == ["male", "female"]


#----------------------------------------------------------------------------------------------------------------------#
#                                             INVALID CASES
#----------------------------------------------------------------------------------------------------------------------#

def test_property_invalid_multiple_expr():

    with pytest.raises(Exception):
        parse(INVALID_BODY_MULTIPLE_EXPRESSION)


def test_property_missing_expr():

    with pytest.raises(Exception):
        parse(INVALID_BODY_MISSING_EXPRESSION)