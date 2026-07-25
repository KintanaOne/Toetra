import pytest
from lark import Tree

from dsl.ast.nodes.assertion import (
    AndNode,
    OrNode,
    NotNode,
    ImplicationNode,
    AssertionNode,
    ComparisonNode,
    ProblemNode,
)
from dsl.builder.program import parse_program
from dsl.language.vocabulary.problems import EnumProblem
from dsl.parser.parser import parse_toetra_code

from test.fixtures.logic_samples import (
    INVALID_LOGIC_SYNTAX,
    INVALID_PARENTHESES,
    NESTED_IMPLICATION_PROPERTY,
    NOT_PRECEDENCE_PROPERTY,
    OPERATOR_PRECEDENCE_PROPERTY,
    PARENTHESES_PRECEDENCE_PROPERTY,
    SIMPLE_LOGIC_PROPERTY,
    SIMPLE_PROBLEM_PROPERTY,
    VALID_IMPLICATION_PROPERTY,
)

# ----------------------------------------------------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------------------------------------------------


def parse(code: str) -> Tree:
    return parse_toetra_code(code)


def build(code: str):
    return parse_program(parse(code)).body[0]


# ----------------------------------------------------------------------------------------------------------------------
# BASIC
# ----------------------------------------------------------------------------------------------------------------------


def test_simple_logic_in_property():

    prop = build(SIMPLE_LOGIC_PROPERTY)

    scope = prop.rule.scope
    assertion = prop.rule.assertion.root

    assert scope is not None
    assert assertion is not None

    match assertion:
        case AndNode(operands=ops):
            assert len(ops) == 2
            assert all(isinstance(op, ComparisonNode) for op in ops)

        case _:
            pytest.fail("Expected AND of two comparisons")


def test_simple_problem_in_property():

    prop = build(SIMPLE_PROBLEM_PROPERTY)

    assertion = prop.rule.assertion.root

    match assertion:
        case ProblemNode(problem=problem):
            assert problem == EnumProblem.CLASSIFICATION

        case _:
            pytest.fail(f"Unexpected node: {assertion}")


# ----------------------------------------------------------------------------------------------------------------------
# PRECEDENCE
# ----------------------------------------------------------------------------------------------------------------------


def test_logic_operator_precedence():
    """
    A OR (B AND C)
    """

    prop = build(OPERATOR_PRECEDENCE_PROPERTY)
    assertion = prop.rule.assertion.root

    match assertion:
        case OrNode(operands=ops):
            assert len(ops) == 2

            left, right = ops

            assert isinstance(left, ComparisonNode)
            assert isinstance(right, AndNode)
            assert len(right.operands) == 2

        case _:
            pytest.fail(f"Unexpected structure: {assertion}")


def test_logic_parentheses_override_precedence():
    """
    (A OR B) AND C
    """

    prop = build(PARENTHESES_PRECEDENCE_PROPERTY)
    assertion = prop.rule.assertion.root

    match assertion:
        case AndNode(operands=ops):
            assert len(ops) == 2

            left, right = ops

            assert isinstance(left, OrNode)
            assert len(left.operands) == 2
            assert isinstance(right, ComparisonNode)

        case _:
            pytest.fail(f"Unexpected structure: {assertion}")


def test_logic_not_precedence():
    """
    NOT A AND B => (NOT A) AND B
    """

    prop = build(NOT_PRECEDENCE_PROPERTY)
    assertion = prop.rule.assertion.root

    match assertion:
        case AndNode(operands=ops):
            assert len(ops) == 2

            left, right = ops

            assert isinstance(left, NotNode)
            assert isinstance(left.operand, ComparisonNode)
            assert isinstance(right, ComparisonNode)

        case _:
            pytest.fail(f"Unexpected structure: {assertion}")


# ----------------------------------------------------------------------------------------------------------------------
# IMPLICATION
# ----------------------------------------------------------------------------------------------------------------------


def test_logic_implication():

    prop = build(VALID_IMPLICATION_PROPERTY)

    assertion = prop.rule.assertion

    assert isinstance(assertion.root, ImplicationNode)

    left = assertion.root.left
    right = assertion.root.right

    assert isinstance(left, ComparisonNode)
    assert isinstance(right, ComparisonNode)


def test_logic_nested_implication():

    prop = build(NESTED_IMPLICATION_PROPERTY)
    assertion = prop.rule.assertion

    match assertion:
        case AssertionNode(
            root=ImplicationNode(left=_, right=ImplicationNode(left=_, right=_))
        ):
            pass

        case _:
            pytest.fail("Expected nested implication")


# ----------------------------------------------------------------------------------------------------------------------
# INVALID
# ----------------------------------------------------------------------------------------------------------------------


def test_invalid_logic_syntax():
    with pytest.raises(Exception):
        build(INVALID_LOGIC_SYNTAX)


def test_invalid_parentheses():
    with pytest.raises(Exception):
        build(INVALID_PARENTHESES)
