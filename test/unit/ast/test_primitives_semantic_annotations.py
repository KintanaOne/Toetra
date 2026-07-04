from dsl.ast.nodes.base import ASTNode
from dsl.ast.nodes.primitives import ArgNode, AttributeNode, ConstantNode
from dsl.semantic.runtime.annotations import SemanticAnnotations
from dsl.semantic.types.enums import EnumDataType


def test_attribute_node_is_semantic_ast_node():
    node = AttributeNode(
        entity="x0",
        feature="age",
        path=["x0", "age"],
    )

    assert isinstance(node, ASTNode)
    assert hasattr(node, "semantic")
    assert node.semantic is None


def test_attribute_node_accepts_semantic_annotations():
    node = AttributeNode(
        entity="x0",
        feature="age",
        path=["x0", "age"],
    )

    node.semantic = SemanticAnnotations()
    node.semantic.resolved_entity = "x0"
    node.semantic.resolved_path = ["x0", "age"]
    node.semantic.resolved_type = "float"

    assert node.semantic is not None
    assert node.semantic.resolved_entity == "x0"
    assert node.semantic.resolved_path == ["x0", "age"]
    assert node.semantic.resolved_type == "float"


def test_constant_node_is_semantic_ast_node():
    node = ConstantNode(
        value=42,
        dtype=EnumDataType.INT,
    )

    assert isinstance(node, ASTNode)
    assert hasattr(node, "semantic")
    assert node.semantic is None


def test_arg_node_is_semantic_ast_node():
    node = ArgNode(
        key="eps",
        value=0.01,
    )

    assert isinstance(node, ASTNode)
    assert hasattr(node, "semantic")
    assert node.semantic is None


def test_primitive_constructors_are_not_polluted_by_semantic_field():
    attr = AttributeNode(
        entity="x0",
        feature="age",
        path=["x0", "age"],
    )

    const = ConstantNode(
        value=1,
        dtype=EnumDataType.INT,
    )

    arg = ArgNode(
        key="eps",
        value=0.01,
    )

    assert attr.entity == "x0"
    assert attr.feature == "age"
    assert attr.path == ["x0", "age"]

    assert const.value == 1
    assert const.dtype is EnumDataType.INT

    assert arg.key == "eps"
    assert arg.value == 0.01