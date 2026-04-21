from pathlib import Path

import pytest
from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code
from test.fixtures.properties_samples import VALID_MINIMAL_EXISTS, VALID_EXISTS_WITH_DOMAIN
from dsl.builder.core.utils import *


def parse(code: str) -> Tree:
    return parse_forml_code(code)

#----------------------------------------------------------------------------------------------------------------------#
#                                             VALID CASES
#----------------------------------------------------------------------------------------------------------------------#

def test_exists_basic():
    """ E1 : Test parsing of an exists expression with domain."""

    tree = parse(VALID_MINIMAL_EXISTS)
    program = parse_program(tree)
    property = program.body[0]

    left = property.implication.left
    right = property.implication.right
    abstractor = property.backend
    
    assert property.type == "ROBUSTNESS"
    assert left.quantifier == "exists"
    assert left.domain == None
    assert right is not None
    assert abstractor is None


def test_exists_with_domain():
    """ E2 : Test parsing of an exists expression with domain."""

    tree = parse(VALID_EXISTS_WITH_DOMAIN)
    program = parse_program(tree)
    property = program.body[0]

    left = property.implication.left
    domain = left.domain
    right = property.implication.right
    backend = property.backend
    
    assert property.type == "ROBUSTNESS"
    assert left.quantifier == "exists"
    assert domain.name == "gender"
    assert domain.values == ["male", "female"]
    assert right is not None
    assert backend is None

#----------------------------------------------------------------------------------------------------------------------#
#                                             INVALID CASES
#----------------------------------------------------------------------------------------------------------------------#


#----------------------------------------------------------------------------------------------------------------------#
#                                             EDGE CASES
#----------------------------------------------------------------------------------------------------------------------#
