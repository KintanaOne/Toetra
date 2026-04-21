from pathlib import Path

import pytest
from lark import Tree

from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code
from test.fixtures.properties_samples import (
    VALID_MINIMAL_FORALL,
    VALID_FORALL_WITH_DOMAIN,
)


def parse(code: str) -> Tree:
    return parse_forml_code(code)


# ----------------------------------------------------------------------------------------------------------------------
#                                             VALID CASES
# ----------------------------------------------------------------------------------------------------------------------

def test_forall_basic():
    """ F1 : Test parsing of a basic forall expression."""

    tree = parse(VALID_MINIMAL_FORALL)
    program = parse_program(tree)
    property = program.body[0]

    left = property.implication.left
    right = property.implication.right
    abstractor = property.backend
    
    assert property.type == "ROBUSTNESS"
    assert left.quantifier == "forall"
    assert left.domain == None
    assert right is not None
    assert abstractor is None


def test_forall_with_domain():
    """ F2 : Test parsing of an forall expression with domain."""

    tree = parse(VALID_FORALL_WITH_DOMAIN)
    program = parse_program(tree)
    property = program.body[0]

    left = property.implication.left
    domain = left.domain
    right = property.implication.right
    backend = property.backend
    
    assert property.type == "ROBUSTNESS"
    assert left.quantifier == "forall"
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
