from lark import Tree
import pytest
from lark.exceptions import UnexpectedToken

from dsl.parser.parser import parse_forml_code
from dsl.builder.core.utils import find_node

from test.fixtures.logic_samples import (
    INVALID_LOGIC_SYNTAX,
    INVALID_PARENTHESES,
    NESTED_IMPLICATION_PROPERTY,
    NOT_PRECEDENCE_PROPERTY,
    OPERATOR_PRECEDENCE_PROPERTY,
    PARENTHESES_PRECEDENCE_PROPERTY,
    SIMPLE_LOGIC_PROPERTY
)

# ----------------------------------------------------------------------------------------------------------------------
# Helpers (test-side only)
# ----------------------------------------------------------------------------------------------------------------------

def parse(code: str) -> Tree:
    return parse_forml_code(code)


def get_assertion(tree: Tree) -> Tree:
    """
    Retrieve the assertion expression node.
    """
    return find_node(tree, "assertion")


def get_assertion_expr(tree: Tree) -> Tree:
    """
    Return the logical expression inside assertion.
    """
    assertion = find_node(tree, "assertion")
    assert assertion is not None, "No assertion node found"

    assert len(assertion.children) == 1, "Assertion should wrap exactly one expression"

    return assertion.children[0]


def is_node(node: Tree, name: str) -> bool:
    return isinstance(node, Tree) and node.data == name


def get_children(node: Tree):
    return [c for c in node.children if isinstance(c, Tree)]


def assert_is_atom(node):
    assert node.data in {"logic_not", "atom", "logic_expr"}


# ----------------------------------------------------------------------------------------------------------------------
# BASIC
# ----------------------------------------------------------------------------------------------------------------------

def test_simple_logic_in_property():
    tree = parse(SIMPLE_LOGIC_PROPERTY)
    assert tree is not None


# ----------------------------------------------------------------------------------------------------------------------
# PRECEDENCE
# ----------------------------------------------------------------------------------------------------------------------

def test_logic_operator_precedence():
    """
    A OR (B AND C)
    """

    tree = parse(OPERATOR_PRECEDENCE_PROPERTY)
    expr = get_assertion_expr(tree)

    assert expr.data == "logic_or"

    left, right = get_children(expr)

    # A
    assert_is_atom(left)

    # B AND C
    assert right.data == "logic_and"
    b, c = get_children(right)

    assert_is_atom(b)
    assert_is_atom(c)


def test_logic_parentheses_override_precedence():
    """
    (A OR B) AND C
    """

    tree = parse(PARENTHESES_PRECEDENCE_PROPERTY)
    assertion = get_assertion(tree)

    assert assertion.data == "logic_and"

    left = get_children(assertion)[0]

    # left should contain OR
    assert left.data == "logic_or"


def test_logic_not_precedence():
    """
    NOT A AND B => (NOT A) AND B
    """

    tree = parse(NOT_PRECEDENCE_PROPERTY)
    assertion = get_assertion(tree)

    assert assertion.data == "logic_and"

    left = get_children(assertion)[0]

    assert left.data == "logic_not"


# ----------------------------------------------------------------------------------------------------------------------
# IMPLICATION
# ----------------------------------------------------------------------------------------------------------------------

def test_logic_implication():
    tree = parse("""
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 =>
        x0.a <= 1 -> x0.b <= 2
    """)

    assertion = get_assertion(tree)

    assert assertion.data == "implication"

    left, right = get_children(assertion)

    assert left is not None
    assert right is not None


def test_logic_nested_implication():

    tree = parse(NESTED_IMPLICATION_PROPERTY)

    assertion = get_assertion(tree)

    assert assertion.data == "implication"

    _, right = get_children(assertion)

    assert right.data == "implication"


# ----------------------------------------------------------------------------------------------------------------------
# INVALID
# ----------------------------------------------------------------------------------------------------------------------

def test_invalid_logic_syntax():
    with pytest.raises(UnexpectedToken):
        parse(INVALID_LOGIC_SYNTAX)


def test_invalid_parentheses():
    with pytest.raises(UnexpectedToken):
        parse(INVALID_PARENTHESES)