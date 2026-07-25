from dsl.ast.nodes.assertion import ComparisonNode
from dsl.ast.nodes.primitives import (
    AttributeNode,
    BinaryArithmeticNode,
    ConstantNode,
    NameRefNode,
    TargetRefNode,
)
from dsl.builder.program import parse_program
from dsl.language.vocabulary.operators import EnumArithmeticOperator
from dsl.parser.parser import parse_toetra_code


def _build(source: str):
    return parse_program(parse_toetra_code(source))


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


def test_builds_bare_name_as_unresolved_name_reference():
    comparison = _build_comparison("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 => age <= 30
        """)

    assert comparison.left == NameRefNode(name="age")

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


def test_builder_preserves_arithmetic_precedence():
    source = """
    model := "model.onnx"
    target := MyTarget

    [LOGIC]:
    forall x0 => x0.a + 2 * x0.b <= target
    """

    comparison = _build_comparison(source)

    assert isinstance(comparison.left, BinaryArithmeticNode)
    assert comparison.left.operator is EnumArithmeticOperator.ADD
    assert comparison.left.left == AttributeNode(
        entity="x0",
        feature="a",
        path=["x0", "a"],
    )

    multiplication = comparison.left.right
    assert isinstance(multiplication, BinaryArithmeticNode)
    assert multiplication.operator is EnumArithmeticOperator.MUL
    assert isinstance(multiplication.left, ConstantNode)
    assert multiplication.left.value == 2
    assert multiplication.right == AttributeNode(
        entity="x0",
        feature="b",
        path=["x0", "b"],
    )

    assert isinstance(comparison.right, TargetRefNode)
