from dsl.ast.nodes.assertion import AndNode, ComparisonNode, OrNode
from dsl.ast.nodes.primitives import AttributeNode
from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code
from dsl.semantic.core.validator import FORMLValidator
from dsl.semantic.runtime.annotations import SemanticAnnotations
from dsl.semantic.runtime.tracer import ValidationTracer


def _build_and_validate(source: str):
    cst = parse_forml_code(source)
    ast = parse_program(cst)

    FORMLValidator().validate(
        ast,
        tracer=ValidationTracer(enabled=False),
    )

    return ast


def _semantic(attr: AttributeNode) -> SemanticAnnotations:
    semantic = attr.semantic

    assert semantic is not None

    return semantic


def _collect_comparisons(node: object) -> list[ComparisonNode]:
    if isinstance(node, ComparisonNode):
        return [node]

    if isinstance(node, AndNode):
        result: list[ComparisonNode] = []

        for child in node.operands:
            result.extend(_collect_comparisons(child))

        return result

    if isinstance(node, OrNode):
        result: list[ComparisonNode] = []

        for child in node.operands:
            result.extend(_collect_comparisons(child))

        return result

    return []


def _left_attribute(node: ComparisonNode) -> AttributeNode:
    left = node.left

    assert isinstance(left, AttributeNode)

    return left


def test_check_at_attribute_receives_semantic_annotations():
    source = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    forall x0 => x0.age <= 30
    """

    ast = _build_and_validate(source)

    root = ast.body[0].rule.assertion.root
    comparison = _collect_comparisons(root)[0]
    attr = _left_attribute(comparison)
    semantic = _semantic(attr)

    assert semantic.resolved_entity == "x0"
    assert semantic.resolved_path == ["x0", "age"]


def test_check_at_implicit_attribute_receives_default_entity():
    source = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    forall x0 => age <= 30
    """

    ast = _build_and_validate(source)

    root = ast.body[0].rule.assertion.root
    comparison = _collect_comparisons(root)[0]
    attr = _left_attribute(comparison)
    semantic = _semantic(attr)

    assert attr.entity is None
    assert attr.feature == "age"
    assert semantic.resolved_entity == "x0"
    assert semantic.resolved_path == ["x0", "age"]


def test_quantifier_attribute_receives_symbolic_entity():
    source = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    forall x0 => age <= 30
    """

    ast = _build_and_validate(source)

    root = ast.body[0].rule.assertion.root
    comparison = _collect_comparisons(root)[0]
    attr = _left_attribute(comparison)
    semantic = _semantic(attr)

    assert semantic.resolved_entity == "x0"
    assert semantic.resolved_path == ["x0", "age"]


def test_nested_logic_attributes_receive_semantic_annotations():
    source = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    forall x0 => (x0.age <= 30 OR x0.income >= 1000) AND x0.score <= 1
    """

    ast = _build_and_validate(source)

    root = ast.body[0].rule.assertion.root
    comparisons = _collect_comparisons(root)

    resolved: dict[str, str | None] = {}

    for comparison in comparisons:
        attr = _left_attribute(comparison)
        semantic = _semantic(attr)

        resolved[attr.feature] = semantic.resolved_entity

    assert resolved == {
        "age": "x0",
        "income": "x0",
        "score": "x0",
    }
