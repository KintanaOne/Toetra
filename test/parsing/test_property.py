import pytest
from lark import Tree

from forml.parser.parser import parse_forml_code
from forml.ast.queries import (
    get_all_properties,
    get_property_dict,
)


def parse(code: str) -> Tree:
    return parse_forml_code(code)


#----------------------------------------------------------------------------------------------------------------------#
#                                             FORALL
#----------------------------------------------------------------------------------------------------------------------#

def test_property_with_quantifier():
    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    forall with gender("male","female") -> CLASSIFICATION.EQUAL()
    """

    tree = parse(code)

    prop = get_all_properties(tree)[0]
    data = get_property_dict(prop)

    assert data["mode"] == "quantifier"
    assert data["quantifier"] == "forall"
    assert data["domain"]["name"] == "gender"
    assert data["domain"]["values"] == ["male", "female"]


#----------------------------------------------------------------------------------------------------------------------#
#                                             AT
#----------------------------------------------------------------------------------------------------------------------#

def test_property_with_at():
    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at x0 in neighborhood(L2, eps=0.01)
    -> CLASSIFICATION.EQUAL()
    """

    tree = parse(code)

    prop = get_all_properties(tree)[0]
    data = get_property_dict(prop)

    assert data["mode"] == "at"
    assert data["neighborhood"]["metric"] == "L2"
    assert data["neighborhood"]["args"]["eps"] == "0.01"


#----------------------------------------------------------------------------------------------------------------------#
#                                             CHECK_AT
#----------------------------------------------------------------------------------------------------------------------#

def test_property_with_check_at():
    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 -> CLASSIFICATION.EQUAL()
    """

    tree = parse(code)

    prop = get_all_properties(tree)[0]
    data = get_property_dict(prop)

    assert data["mode"] == "check_at"


#----------------------------------------------------------------------------------------------------------------------#
#                                             PAIRWISE
#----------------------------------------------------------------------------------------------------------------------#

def test_property_with_pairwise():
    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) -> CLASSIFICATION.EQUAL()
    """

    tree = parse(code)

    prop = get_all_properties(tree)[0]
    data = get_property_dict(prop)

    assert data["mode"] == "pairwise"
    assert data["neighborhood"]["metric"] == "L2"


#----------------------------------------------------------------------------------------------------------------------#
#                                             DOMAIN
#----------------------------------------------------------------------------------------------------------------------#

def test_property_with_domain():
    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    forall with gender("male","female") -> CLASSIFICATION.EQUAL()
    """

    tree = parse(code)

    prop = get_all_properties(tree)[0]
    data = get_property_dict(prop)

    assert data["domain"]["name"] == "gender"
    assert data["domain"]["values"] == ["male", "female"]


#----------------------------------------------------------------------------------------------------------------------#
#                                             INVALID CASES
#----------------------------------------------------------------------------------------------------------------------#

def test_property_invalid_multiple_expr():
    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    forall at x0 -> CLASSIFICATION.EQUAL()
    """

    with pytest.raises(Exception):
        parse(code)


def test_property_missing_expr():
    code = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    -> CLASSIFICATION.EQUAL()
    """

    with pytest.raises(Exception):
        parse(code)