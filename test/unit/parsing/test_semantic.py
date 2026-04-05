from lark import Tree
import pytest

from forml.parser.parser import parse_forml_code
from forml.ast.queries import get_program_dict
from test.fixtures.program_samples import INVALID_BODY_MISSING_EXPRESSION, INVALID_BODY_MULTIPLE_EXPRESSION, VALID_PROGRAM_WITH_BODY_MULTIPLE_PROPERTIES
from test.fixtures.properties_samples import (
    VALID_AT_WITH_NEIGHBORHOOD,
    VALID_AT_WITH_NEIGHBORHOOD_AND_DOMAIN,
    VALID_FORALL_WITH_DOMAIN,
    VALID_MINIMAL_CHECK_AT,
    VALID_PAIRWISE_WITH_ABSTRACTOR
)


def parse(code: str) -> Tree:
    return parse_forml_code(code)


#----------------------------------------------------------------------------------------------------------------------#
#                                             HEADER
#----------------------------------------------------------------------------------------------------------------------#

def test_program_header():

    data = get_program_dict(parse(VALID_AT_WITH_NEIGHBORHOOD))

    assert data["model"] == "model.onnx"
    assert data["target"] == "MyTarget"


#----------------------------------------------------------------------------------------------------------------------#
#                                             AT
#----------------------------------------------------------------------------------------------------------------------#

def test_program_with_at():

    data = get_program_dict(parse(VALID_AT_WITH_NEIGHBORHOOD))
    prop = data["properties"][0]

    assert prop["type"] == "ROBUSTNESS"
    assert prop["mode"] == "at"

    assert prop["neighborhood"]["metric"] == "L2"
    assert prop["neighborhood"]["args"]["eps"] == "0.01"


#----------------------------------------------------------------------------------------------------------------------#
#                                             CHECK_AT
#----------------------------------------------------------------------------------------------------------------------#

def test_program_with_check_at():

    data = get_program_dict(parse(VALID_MINIMAL_CHECK_AT))
    prop = data["properties"][0]

    assert prop["mode"] == "check_at"


#----------------------------------------------------------------------------------------------------------------------#
#                                             PAIRWISE
#----------------------------------------------------------------------------------------------------------------------#

def test_program_with_pairwise():

    data = get_program_dict(parse(VALID_PAIRWISE_WITH_ABSTRACTOR))
    prop = data["properties"][0]

    assert prop["mode"] == "pairwise"

    assert prop["neighborhood"]["metric"] == "L2"
    assert prop["abstractor"]["name"] == "Z3"


#----------------------------------------------------------------------------------------------------------------------#
#                                             QUANTIFIER
#----------------------------------------------------------------------------------------------------------------------#

def test_program_with_quantifier():

    data = get_program_dict(parse(VALID_FORALL_WITH_DOMAIN))
    prop = data["properties"][0]

    assert prop["mode"] == "quantifier"
    assert prop["quantifier"] == "forall"

    assert prop["domain"]["name"] == "gender"
    assert prop["domain"]["values"] == ["male", "female"]


#----------------------------------------------------------------------------------------------------------------------#
#                                             MULTIPLE PROPERTIES
#----------------------------------------------------------------------------------------------------------------------#

def test_program_multiple_properties():

    data = get_program_dict(parse(VALID_PROGRAM_WITH_BODY_MULTIPLE_PROPERTIES))

    assert len(data["properties"]) == 2

    assert data["properties"][0]["mode"] == "at"
    assert data["properties"][1]["mode"] == "quantifier"


#----------------------------------------------------------------------------------------------------------------------#
#                                             DOMAIN + NEIGHBORHOOD
#----------------------------------------------------------------------------------------------------------------------#

def test_program_with_domain_and_neighborhood():

    data = get_program_dict(parse(VALID_AT_WITH_NEIGHBORHOOD_AND_DOMAIN))
    prop = data["properties"][0]

    assert prop["domain"]["name"] == "sex"
    assert prop["domain"]["values"] == ["male", "female"]

    assert prop["neighborhood"]["metric"] == "L2"


#----------------------------------------------------------------------------------------------------------------------#
#                                             INVALID CASES
#----------------------------------------------------------------------------------------------------------------------#

def test_invalid_multiple_expr():

    with pytest.raises(Exception):
        parse(INVALID_BODY_MULTIPLE_EXPRESSION)


def test_invalid_missing_expr():

    with pytest.raises(Exception):
        parse(INVALID_BODY_MISSING_EXPRESSION)