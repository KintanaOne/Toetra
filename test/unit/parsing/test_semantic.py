from lark import Tree
import pytest

from dsl.builder.expressions import parse_at
from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code
from previous_forml.ast.queries import get_program_dict
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

    tree = parse(VALID_AT_WITH_NEIGHBORHOOD)

    data = parse_program(tree)

    assert data["model"] == "model.onnx"
    assert data["target"] == "MyTarget"


#----------------------------------------------------------------------------------------------------------------------#
#                                             AT
#----------------------------------------------------------------------------------------------------------------------#

def test_program_with_at():

    tree = parse(VALID_AT_WITH_NEIGHBORHOOD)
    program = parse_program(tree)

    property = program["properties"][0]
    expr = property["expr"]
    neighborhood = expr["neighborhood"]

    assert program["model"] is not None
    assert program["target"] is not None

    assert property["type"] == "ROBUSTNESS"
    assert expr["kind"] == "at"
    assert property["assertion"] is not None

    assert neighborhood["metric"] == "L2"
    assert neighborhood["args"]["eps"] == 0.01

    assert property["abstractor"] is None


#----------------------------------------------------------------------------------------------------------------------#
#                                             CHECK_AT
#----------------------------------------------------------------------------------------------------------------------#

def test_program_with_check_at():

    tree = parse(VALID_MINIMAL_CHECK_AT)
    program = parse_program(tree)

    property = program["properties"][0]
    expr = property["expr"]

    assert program["model"] is not None
    assert program["target"] is not None

    assert property["type"] == "ROBUSTNESS"
    assert expr["kind"] == "check_at"
    assert property["assertion"] is not None

    assert property["abstractor"] is None

#----------------------------------------------------------------------------------------------------------------------#
#                                             PAIRWISE
#----------------------------------------------------------------------------------------------------------------------#

def test_program_with_pairwise():

    tree = parse(VALID_PAIRWISE_WITH_ABSTRACTOR)
    program = parse_program(tree)

    property = program["properties"][0]
    expr = property["expr"]
    neighborhood = expr["neighborhood"]

    assert program["model"] is not None
    assert program["target"] is not None

    assert property["type"] == "ROBUSTNESS"
    assert expr["kind"] == "pairwise"
    assert property["assertion"] is not None

    assert neighborhood["metric"] == "L2"
    assert neighborhood["args"]["eps"] == 0.01

    assert property["abstractor"] is not None

#----------------------------------------------------------------------------------------------------------------------#
#                                             QUANTIFIER
#----------------------------------------------------------------------------------------------------------------------#

def test_program_with_quantifier():

    tree = parse(VALID_FORALL_WITH_DOMAIN)
    program = parse_program(tree)

    property = program["properties"][0]
    expr = property["expr"]
    domain = expr["domain"]

    assert program["model"] is not None
    assert program["target"] is not None

    assert property["type"] == "ROBUSTNESS"
    assert expr["kind"] == "quantifier"
    assert property["assertion"] is not None

    assert domain["name"] == "gender"
    assert domain["values"] == ["male", "female"]

    assert property["abstractor"] is None

#----------------------------------------------------------------------------------------------------------------------#
#                                             MULTIPLE PROPERTIES
#----------------------------------------------------------------------------------------------------------------------#

def test_program_multiple_properties():

    tree = parse(VALID_PROGRAM_WITH_BODY_MULTIPLE_PROPERTIES)
    program = parse_program(tree)

    assert len(program["properties"]) == 2

    assert program["properties"][0]["expr"]["kind"] == "at"
    assert program["properties"][1]["expr"]["kind"] == "quantifier"


#----------------------------------------------------------------------------------------------------------------------#
#                                             DOMAIN + NEIGHBORHOOD
#----------------------------------------------------------------------------------------------------------------------#

def test_program_with_domain_and_neighborhood():

    tree = parse(VALID_AT_WITH_NEIGHBORHOOD_AND_DOMAIN)
    program = parse_program(tree)

    property = program["properties"][0]
    expr = property["expr"]
    neighborhood = expr["neighborhood"]
    domain = expr["domain"]

    assert program["model"] is not None
    assert program["target"] is not None

    assert property["type"] == "ROBUSTNESS"
    assert expr["kind"] == "at"
    assert property["assertion"] is not None

    assert neighborhood["metric"] == "L2"
    assert neighborhood["args"]["eps"] == 0.01

    assert domain["name"] == "sex"
    assert domain["values"] == ["male", "female"]

    assert property["abstractor"] is None


#----------------------------------------------------------------------------------------------------------------------#
#                                             INVALID CASES
#----------------------------------------------------------------------------------------------------------------------#

def test_invalid_multiple_expr():

    with pytest.raises(Exception):
        parse(INVALID_BODY_MULTIPLE_EXPRESSION)


def test_invalid_missing_expr():

    with pytest.raises(Exception):
        parse(INVALID_BODY_MISSING_EXPRESSION)