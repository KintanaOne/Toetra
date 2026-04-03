from pathlib import Path

import pytest
from forml.ast.queries import get_program_dict
from forml.parser.parser import parse_forml_code
from test.utils import *


def parse(code: str) -> Tree:
    return parse_forml_code(code)

#----------------------------------------------------------------------------------------------------------------------#
#                                             VALID CASES
#----------------------------------------------------------------------------------------------------------------------#

def test_exists_basic():
    """ E1 : Test parsing of a basic exists expression."""

    code="""
    # This is a comment
    # Another comment
    model := "path/to/model.onnx"
    target := MyTargetColumn

    # 1 exists without using
    [ROBUSTNESS]:
    exists with gender("male", "female") -> x.target == 0
    """

    tree = parse(code)

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
