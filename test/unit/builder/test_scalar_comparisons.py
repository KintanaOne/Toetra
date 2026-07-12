import pytest

from dsl.ast.nodes.assertion import ComparisonNode
from dsl.ast.nodes.primitives import (
    AttributeNode,
    ConstantNode,
    TargetRefNode,
)
from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code


def _build(source: str):
    return parse_program(parse_forml_code(source))


def _build_comparison(source: str) -> ComparisonNode:
    program = _build(source)
    root = program.body[0].rule.assertion.root

    assert isinstance(root, ComparisonNode)

    return root


def test_builds_target_to_constant_comparison_from_scalar_cst():
    comparison = _build_comparison("""
        model := "model.onnx"
        target := MyTarget

        [BOUND]:
        check_at x0 => target <= 10
        """)

    assert isinstance(comparison.left, TargetRefNode)
    assert isinstance(comparison.right, ConstantNode)
    assert comparison.right.value == 10


def test_builds_implicit_attribute_to_constant_comparison():
    comparison = _build_comparison("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 => age <= 30
        """)

    assert isinstance(comparison.left, AttributeNode)
    assert comparison.left.entity is None
    assert comparison.left.feature == "age"

    assert isinstance(comparison.right, ConstantNode)


def test_builder_preserves_symmetric_attribute_to_target_comparison():
    comparison = _build_comparison("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 => x0.score <= target
        """)

    assert isinstance(comparison.left, AttributeNode)
    assert comparison.left.entity == "x0"
    assert comparison.left.feature == "score"

    assert isinstance(comparison.right, TargetRefNode)


def test_arithmetic_is_parsed_by_g1_but_deferred_by_g2a_builder():
    source = """
    model := "model.onnx"
    target := MyTarget

    [LOGIC]:
    forall x0 => x0.a + 2 * x0.b <= target
    """

    with pytest.raises(NotImplementedError, match="G2-A"):
        _build(source)
