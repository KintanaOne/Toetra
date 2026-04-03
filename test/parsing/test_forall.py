from pathlib import Path

import pytest
from lark import Tree

from forml.ast.queries import get_program_dict
from forml.parser.parser import parse_forml_code


def parse(code: str) -> Tree:
    return parse_forml_code(code)


# ----------------------------------------------------------------------------------------------------------------------
#                                             VALID CASES
# ----------------------------------------------------------------------------------------------------------------------

def test_forall_basic():
    """ F1 : Test parsing of a basic forall expression."""
    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    forall with gender("male", "female") -> x.target == 0
    """

    tree = parse(code)

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
