import pytest
from lark import Tree

from forml.parser.parser import parse_forml_code
from forml.ast.queries import (
    get_header,
    get_model_declaration,
    get_target_declaration,
)

def parse(code: str) -> Tree:
    return parse_forml_code(code)

def test_header_valid():
    code = """
    model := "model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) -> CLASSIFICATION.EQUAL()
    """

    tree = parse(code)

    header = get_header(tree)
    assert header is not None

    model = get_model_declaration(tree)
    target = get_target_declaration(tree)

    assert model is not None
    assert target is not None

def test_header_missing_model():
    code = """
    target := MyTargetColumn

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) -> CLASSIFICATION.EQUAL()
    """

    with pytest.raises(Exception):
        parse(code)

def test_header_missing_target():
    code = """
    model := "model.onnx"

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) -> CLASSIFICATION.EQUAL()
    """

    with pytest.raises(Exception):
        parse(code)

def test_header_missing_both():
    code = """
    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) -> CLASSIFICATION.EQUAL()
    """

    with pytest.raises(Exception):
        parse(code)

def test_header_invalid_model_type():
    code = """
    model := 12345
    target := MyTargetColumn

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) -> CLASSIFICATION.EQUAL()
    """

    with pytest.raises(Exception):
        parse(code)

def test_header_invalid_target_type():
    code = """
    model := "model.onnx"
    target := 12345

    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) -> CLASSIFICATION.EQUAL()
    """

    with pytest.raises(Exception):
        parse(code)

def test_header_with_comments():
    code = """
    # comments are ignored

    model := "model.onnx"
    target := MyTargetColumn

    # between declarations
    [ROBUSTNESS]:
    x ~ x' in neighborhood(L2, eps=0.01) -> CLASSIFICATION.EQUAL()
    """

    tree = parse(code)

    assert get_header(tree) is not None
    assert get_model_declaration(tree) is not None
    assert get_target_declaration(tree) is not None