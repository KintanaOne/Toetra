from lark import Tree
import pytest
from lark.exceptions import UnexpectedToken

from forml.parser.parser import parse_forml_code
from forml.ast.queries import (
    get_assertion_expression,
    is_implication,
    get_implication_left,
    get_implication_right,
    get_logic_or,
    get_logic_and,
    get_logic_not,
    get_or_operands,
)


def parse(code: str) -> Tree:
    return parse_forml_code(code)


# ----------------------------------------------------------------------------------------------------------------------
#                                             BASIC
# ----------------------------------------------------------------------------------------------------------------------

def test_simple_logic_in_property():
    tree = parse("""
    model := "path/to/model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at x0 -> CLASSIFICATION.EQUAL()
    """)

    assert tree is not None


# ----------------------------------------------------------------------------------------------------------------------
#                                             PRECEDENCE
# ----------------------------------------------------------------------------------------------------------------------

def test_logic_operator_precedence():
    """
    A OR (B AND C)
    """
    tree = parse("""
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 ->
        x0.a <= 1 OR x0.b <= 2 AND x0.c <= 3
    """)

    assertion = get_assertion_expression(tree)

    logic_or = get_logic_or(assertion)
    operands = get_or_operands(logic_or)

    assert len(operands) == 2

    left, right = operands

    assert right.data == "logic_and"


def test_logic_parentheses_override_precedence():
    """
    (A OR B) AND C
    """
    tree = parse("""
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 -> (x0.a <= 1 OR x0.b <= 2) AND x0.c <= 3
    """)

    assertion = get_assertion_expression(tree)

    logic_and = get_logic_and(assertion)

    assert logic_and is not None

    left = logic_and.children[0]

    # left should contain OR inside
    inner_or = get_logic_or(left)
    assert inner_or is not None


def test_logic_not_precedence():
    """
    NOT A AND B => (NOT A) AND B
    """
    tree = parse("""
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 ->
        NOT x0.a <= 1 AND x0.b <= 2
    """)

    assertion = get_assertion_expression(tree)

    logic_and = get_logic_and(assertion)

    left = logic_and.children[0]

    assert left.data == "logic_not"


# ----------------------------------------------------------------------------------------------------------------------
#                                             IMPLICATION
# ----------------------------------------------------------------------------------------------------------------------

def test_logic_implication():
    tree = parse("""
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 ->
        x0.a <= 1 -> x0.b <= 2
    """)

    assertion = get_assertion_expression(tree)

    assert is_implication(assertion)

    left = get_implication_left(assertion)
    right = get_implication_right(assertion)

    assert left is not None
    assert right is not None


def test_logic_nested_implication():
    tree = parse("""
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 ->
        x0.a <= 1 -> x0.b <= 2 -> x0.c <= 3
    """)

    assertion = get_assertion_expression(tree)

    assert is_implication(assertion)

    right = get_implication_right(assertion)

    assert is_implication(right)


# ----------------------------------------------------------------------------------------------------------------------
#                                             INVALID
# ----------------------------------------------------------------------------------------------------------------------

def test_invalid_logic_syntax():
    with pytest.raises(UnexpectedToken):
        parse("""
        model := "model.onnx"
        target := MyTarget

        [ROBUSTNESS]:
        check_at x0 ->
            x0.a <= OR x0.b <= 2
        """)


def test_invalid_parentheses():
    with pytest.raises(UnexpectedToken):
        parse("""
        model := "model.onnx"
        target := MyTarget

        [ROBUSTNESS]:
        check_at x0 ->
            (x0.a <= 1 OR x0.b <= 2
        """)