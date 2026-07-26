from toetra._compiler.ast.nodes.assertion import ComparisonNode
from toetra._compiler.ast.nodes.base import ASTNode
from toetra._compiler.ast.nodes.primitives import (
    AttributeNode,
    BinaryArithmeticNode,
    ConstantNode,
    NameRefNode,
    ScalarExpressionNode,
    TargetRefNode,
    UnaryArithmeticNode,
)
from toetra._language.vocabulary.operators import (
    EnumArithmeticOperator,
    EnumComparisonOperator,
    EnumUnaryOperator,
)
from toetra._compiler.semantic.types.enums import EnumDataType


def test_name_ref_node_is_an_unresolved_scalar_expression() -> None:
    node = NameRefNode(name="minimum_income")

    assert isinstance(node, ASTNode)
    assert isinstance(node, ScalarExpressionNode)
    assert node.name == "minimum_income"
    assert node.semantic is None


def test_unary_arithmetic_node_preserves_operator_and_operand() -> None:
    operand = NameRefNode(name="offset")

    node = UnaryArithmeticNode(
        operator=EnumUnaryOperator.MINUS,
        operand=operand,
    )

    assert isinstance(node, ScalarExpressionNode)
    assert node.operator is EnumUnaryOperator.MINUS
    assert node.operand is operand
    assert node.semantic is None


def test_binary_arithmetic_node_preserves_ordered_operands() -> None:
    left = AttributeNode(
        entity="x0",
        feature="income",
        path=["x0", "income"],
    )
    right = ConstantNode(
        value=2,
        dtype=EnumDataType.INT,
    )

    node = BinaryArithmeticNode(
        left=left,
        operator=EnumArithmeticOperator.DIV,
        right=right,
    )

    assert isinstance(node, ScalarExpressionNode)
    assert node.left is left
    assert node.operator is EnumArithmeticOperator.DIV
    assert node.right is right
    assert node.semantic is None


def test_scalar_expression_family_has_distinct_leaf_kinds() -> None:
    name = NameRefNode(name="threshold")
    attribute = AttributeNode(
        entity="x0",
        feature="threshold",
        path=["x0", "threshold"],
    )
    target = TargetRefNode()

    assert type(name) is NameRefNode
    assert type(attribute) is AttributeNode
    assert type(target) is TargetRefNode


def test_nested_binary_arithmetic_tree_preserves_precedence_shape() -> None:
    multiplication = BinaryArithmeticNode(
        left=NameRefNode(name="b"),
        operator=EnumArithmeticOperator.MUL,
        right=ConstantNode(
            value=2,
            dtype=EnumDataType.INT,
        ),
    )
    addition = BinaryArithmeticNode(
        left=NameRefNode(name="a"),
        operator=EnumArithmeticOperator.ADD,
        right=multiplication,
    )

    assert addition.operator is EnumArithmeticOperator.ADD
    assert isinstance(addition.left, NameRefNode)
    assert addition.right is multiplication
    assert multiplication.operator is EnumArithmeticOperator.MUL


def test_arithmetic_nodes_can_be_comparison_operands() -> None:
    left = BinaryArithmeticNode(
        left=NameRefNode(name="a"),
        operator=EnumArithmeticOperator.ADD,
        right=ConstantNode(
            value=1,
            dtype=EnumDataType.INT,
        ),
    )
    right = BinaryArithmeticNode(
        left=TargetRefNode(),
        operator=EnumArithmeticOperator.SUB,
        right=ConstantNode(
            value=2,
            dtype=EnumDataType.INT,
        ),
    )

    comparison = ComparisonNode(
        left=left,
        op=EnumComparisonOperator.LTE,
        right=right,
    )

    assert comparison.left is left
    assert comparison.right is right
