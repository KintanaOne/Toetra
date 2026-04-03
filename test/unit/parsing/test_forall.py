from pathlib import Path

import pytest
from lark import Tree

from forml.ast.queries import get_program_dict
from forml.parser.parser import parse_forml_code
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

    program = get_program_dict(tree)

    assert program["properties"][0] == {
        "type": "ROBUSTNESS",
        "mode": "quantifier",
        "quantifier": "forall",
        "domain": None,
        "neighborhood": None,
        "abstractor": None,
    }


def test_forall_with_domain():
    """ F2 : Test parsing of an forall expression with domain."""

    tree = parse(VALID_FORALL_WITH_DOMAIN)

    program = get_program_dict(tree)

    assert program["properties"][0] == {
        "type": "ROBUSTNESS",
        "mode": "quantifier",
        "quantifier": "forall",
        "domain": {
            "name": "gender",
            "values": ["male", "female"]
        },
        "neighborhood": None,
        "abstractor": None,
    }



#----------------------------------------------------------------------------------------------------------------------#
#                                             INVALID CASES
#----------------------------------------------------------------------------------------------------------------------#


#----------------------------------------------------------------------------------------------------------------------#
#                                             EDGE CASES
#----------------------------------------------------------------------------------------------------------------------#
