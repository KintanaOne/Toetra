from lark import Tree
import pytest

from forml.parser.parser import parse_forml_code
from forml.ast.queries import get_program_dict


def parse(code: str) -> Tree:
    return parse_forml_code(code)


#----------------------------------------------------------------------------------------------------------------------#
#                                             HEADER
#----------------------------------------------------------------------------------------------------------------------#

def test_program_header():
    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at x0 in neighborhood(L2, eps=0.01) -> CLASSIFICATION.EQUAL()
    """

    data = get_program_dict(parse(code))

    assert data["model"] == "model.onnx"
    assert data["target"] == "MyTarget"


#----------------------------------------------------------------------------------------------------------------------#
#                                             AT
#----------------------------------------------------------------------------------------------------------------------#

def test_program_with_at():
    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at x0 in neighborhood(L2, eps=0.01) -> CLASSIFICATION.EQUAL()
    """

    data = get_program_dict(parse(code))
    prop = data["properties"][0]

    assert prop["type"] == "ROBUSTNESS"
    assert prop["mode"] == "at"

    assert prop["neighborhood"]["metric"] == "L2"
    assert prop["neighborhood"]["args"]["eps"] == "0.01"


#----------------------------------------------------------------------------------------------------------------------#
#                                             CHECK_AT
#----------------------------------------------------------------------------------------------------------------------#

def test_program_with_check_at():
    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 -> x0.a <= 1
    """

    data = get_program_dict(parse(code))
    prop = data["properties"][0]

    assert prop["mode"] == "check_at"


#----------------------------------------------------------------------------------------------------------------------#
#                                             PAIRWISE
#----------------------------------------------------------------------------------------------------------------------#

def test_program_with_pairwise():
    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) -> CLASSIFICATION.EQUAL() using Z3
    """

    data = get_program_dict(parse(code))
    prop = data["properties"][0]

    assert prop["mode"] == "pairwise"

    assert prop["neighborhood"]["metric"] == "L2"
    assert prop["abstractor"]["name"] == "Z3"


#----------------------------------------------------------------------------------------------------------------------#
#                                             QUANTIFIER
#----------------------------------------------------------------------------------------------------------------------#

def test_program_with_quantifier():
    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    forall with gender("male","female") -> CLASSIFICATION.EQUAL()
    """

    data = get_program_dict(parse(code))
    prop = data["properties"][0]

    assert prop["mode"] == "quantifier"
    assert prop["quantifier"] == "forall"

    assert prop["domain"]["name"] == "gender"
    assert prop["domain"]["values"] == ["male", "female"]


#----------------------------------------------------------------------------------------------------------------------#
#                                             MULTIPLE PROPERTIES
#----------------------------------------------------------------------------------------------------------------------#

def test_program_multiple_properties():
    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at x0 -> CLASSIFICATION.EQUAL()

    [FAIRNESS]:
    forall with gender("male","female") -> CLASSIFICATION.EQUAL()
    """

    data = get_program_dict(parse(code))

    assert len(data["properties"]) == 2

    assert data["properties"][0]["mode"] == "at"
    assert data["properties"][1]["mode"] == "quantifier"


#----------------------------------------------------------------------------------------------------------------------#
#                                             DOMAIN + NEIGHBORHOOD
#----------------------------------------------------------------------------------------------------------------------#

def test_program_with_domain_and_neighborhood():
    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at x0 in neighborhood(L2, eps=0.01) with sex("male","female")
    -> CLASSIFICATION.EQUAL()
    """

    data = get_program_dict(parse(code))
    prop = data["properties"][0]

    assert prop["domain"]["name"] == "sex"
    assert prop["domain"]["values"] == ["male", "female"]

    assert prop["neighborhood"]["metric"] == "L2"


#----------------------------------------------------------------------------------------------------------------------#
#                                             INVALID CASES
#----------------------------------------------------------------------------------------------------------------------#

def test_invalid_multiple_expr():
    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    forall at x0 -> CLASSIFICATION.EQUAL()
    """

    with pytest.raises(Exception):
        parse(code)


def test_invalid_missing_expr():
    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    -> CLASSIFICATION.EQUAL()
    """

    with pytest.raises(Exception):
        parse(code)