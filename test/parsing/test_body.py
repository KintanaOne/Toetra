import pytest
from lark import Tree

from forml.parser.parser import parse_forml_code
from forml.ast.queries import (
    get_property_expression,
    get_assertion_expression,
    get_abstractor
)

def parse(code: str) -> Tree:
    return parse_forml_code(code)

def test_body_simple_rule():
    code = """
    model := "model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) -> CLASSIFICATION.EQUAL()
    """

    tree = parse(code)

    property = get_property_expression(tree)

    assertion = get_assertion_expression(tree)

    assert property is not None

    assert assertion is not None

def test_body_with_using():
    code = """
    model := "model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) -> CLASSIFICATION.EQUAL() using eran(param1="a")
    """

    tree = parse(code)

    prop = get_property_expression(tree)

    # abstraction layer exists 
    abstractor = get_abstractor(tree)

    assert abstractor is not None

def test_body_empty():
    code = """
    model := "model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    """

    with pytest.raises(Exception):
        parse(code)

def test_body_syntax_error():
    code = """
    model := "model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) CLASSIFICATION.EQUAL()   # missing ->
    """

    with pytest.raises(Exception):
        parse(code)

def test_body_invalid_assertion():
    code = """
    model := "model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) -> CLASSIFICATION.INVALID()
    """

    with pytest.raises(Exception):
        parse(code)

