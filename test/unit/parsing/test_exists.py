from pathlib import Path

import pytest
from forml.ast.queries import get_program_dict
from forml.parser.parser import parse_forml_code
from test.fixtures.properties_samples import VALID_MINIMAL_EXISTS, VALID_MINIMAL_EXISTS_WITH_DOMAIN
from test.utils import *


def parse(code: str) -> Tree:
    return parse_forml_code(code)

#----------------------------------------------------------------------------------------------------------------------#
#                                             VALID CASES
#----------------------------------------------------------------------------------------------------------------------#

def test_exists_basic():
    """ E1 : Test parsing of an exists expression with domain."""

    tree = parse(VALID_MINIMAL_EXISTS)

    program = get_program_dict(tree)

    assert program["properties"][0] == {
        "type": "ROBUSTNESS",
        "mode": "quantifier",
        "quantifier": "exists",
        "domain": None,
        "neighborhood": None,
        "abstractor": None,
    }


def test_exists_with_domain():
    """ E2 : Test parsing of an exists expression with domain."""

    tree = parse(VALID_MINIMAL_EXISTS_WITH_DOMAIN)

    program = get_program_dict(tree)

    assert program["properties"][0] == {
        "type": "ROBUSTNESS",
        "mode": "quantifier",
        "quantifier": "exists",
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
