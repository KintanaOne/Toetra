from pathlib import Path

import pytest
from forml.ast.program import parse_program
from forml.parser.parser import parse_forml_code
from test.fixtures.properties_samples import VALID_MINIMAL_EXISTS, VALID_EXISTS_WITH_DOMAIN
from forml.core.utils import *


def parse(code: str) -> Tree:
    return parse_forml_code(code)

#----------------------------------------------------------------------------------------------------------------------#
#                                             VALID CASES
#----------------------------------------------------------------------------------------------------------------------#

def test_exists_basic():
    """ E1 : Test parsing of an exists expression with domain."""

    tree = parse(VALID_MINIMAL_EXISTS)
    program = parse_program(tree)
    property = program["properties"][0]

    expr = property["expr"]
    assertion = property["assertion"]
    abstractor = property["abstractor"]
    
    assert property["type"] == "ROBUSTNESS"
    assert expr["kind"] == "quantifier"
    assert expr["quantifier"] == "exists"
    assert expr["domain"] == None
    assert assertion is not None
    assert abstractor is None


def test_exists_with_domain():
    """ E2 : Test parsing of an exists expression with domain."""

    tree = parse(VALID_EXISTS_WITH_DOMAIN)
    program = parse_program(tree)
    property = program["properties"][0]

    expr = property["expr"]
    domain = expr["domain"]
    assertion = property["assertion"]
    abstractor = property["abstractor"]
    
    assert property["type"] == "ROBUSTNESS"
    assert expr["kind"] == "quantifier"
    assert expr["quantifier"] == "exists"
    assert domain["name"] == "gender"
    assert domain["values"] == ["male", "female"]
    assert assertion is not None
    assert abstractor is None



#----------------------------------------------------------------------------------------------------------------------#
#                                             INVALID CASES
#----------------------------------------------------------------------------------------------------------------------#


#----------------------------------------------------------------------------------------------------------------------#
#                                             EDGE CASES
#----------------------------------------------------------------------------------------------------------------------#
