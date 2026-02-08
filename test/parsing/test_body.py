import pytest
from forml.parser.parser import parse_forml_code
from test.utils import *


def test_body_simple_rule():
    code = """
    # This is a comment
    # Another comment
    model := "path/to/model.onnx"
    target := MyTargetColumn

    [ROBUTNESS]:
    forall in hyperball("L2", 0.01) -> CLASSIFICATION.EQUAL();
    """
    result = parse_forml_code(code)
    print(result.pretty())
    body = find_child(result, "body")
    assert body is not None
    properties = find_all(body, "property_section")
    assert len(properties) == 1
    hyperball = find_node(body, "hyperball")
    assert hyperball.data == "hyperball"


def test_body_multiple_rules():
    code = """
    model := "path/to/model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    forall in hyperball("L2", 0.01) -> CLASSIFICATION.EQUAL();

    [ROBUSTNESS]:
    forall in hyperball("L2", 0.05) -> CLASSIFICATION.EQUAL();
    """
    result = parse_forml_code(code)
    properties = find_all_nodes(result, "property_section")
    assert len(properties) == 2
    for p in properties:
        assert p is not None


def test_body_with_using():
    code = """
    model := "path/to/model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    forall in hyperball("L2", 0.01) -> CLASSIFICATION.EQUAL() using eran(param1="a");
    """
    result = parse_forml_code(code)
    body = find_node(result, "body")
    assert body is not None
    abstractor = find_node(body, "abstractor")
    assert abstractor is not None


def test_body_empty():
    code = """
    model := "path/to/model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    """

    with pytest.raises(Exception):
        parse_forml_code(code)


def test_body_syntax_error():
    code = """
    model := "path/to/model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    forall in hyperball("L2", 0.01) CLASSIFICATION.EQUAL();  # missing ->
    """
    with pytest.raises(Exception):
        parse_forml_code(code)


def test_body_invalid_property():
    code = """
    model := "path/to/model.onnx"
    target := MyTargetColumn

    [ROBUSTNESS]:
    forall in hyperball("L2", 0.01) -> CLASSIFICATION.INVALID();
    """
    with pytest.raises(Exception):
        parse_forml_code(code)
