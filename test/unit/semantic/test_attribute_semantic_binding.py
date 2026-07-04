from dsl.ast.nodes.primitives import AttributeNode
from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code
from dsl.semantic.core.validator import FORMLValidator
from dsl.semantic.runtime.annotations import SemanticAnnotations
from dsl.semantic.runtime.tracer import ValidationTracer
from dsl.ast.nodes.assertion import ComparisonNode, AndNode, OrNode


def _build_and_validate(source: str):
    cst = parse_forml_code(source)
    ast = parse_program(cst)

    FORMLValidator().validate(
        ast,
        tracer=ValidationTracer(enabled=False),
    )

    return ast


def _semantic(attr: AttributeNode) -> SemanticAnnotations:
    assert attr.semantic is not None
    return attr.semantic


def _collect_comparisons(node):
    if isinstance(node, ComparisonNode):
        return [node]

    if isinstance(node, AndNode):
        result = []
        for child in node.operands:
            result.extend(_collect_comparisons(child))
        return result

    if isinstance(node, OrNode):
        result = []
        for child in node.operands:
            result.extend(_collect_comparisons(child))
        return result

    return []


def test_check_at_attribute_receives_semantic_annotations():
    source = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 => x0.age <= 30
    """

    ast = _build_and_validate(source)

    root = ast.body[0].rule.assertion.root
    comparison = _collect_comparisons(root)[0]
    attr = comparison.left

    assert attr.semantic is not None
    assert attr.semantic.resolved_entity == "x0"
    assert attr.semantic.resolved_path == ["x0", "age"]


def test_check_at_implicit_attribute_receives_default_entity():
    source = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 => age <= 30
    """

    ast = _build_and_validate(source)

    root = ast.body[0].rule.assertion.root
    comparison = _collect_comparisons(root)[0]
    attr = comparison.left

    assert attr.entity is None
    assert attr.feature == "age"
    assert attr.semantic is not None
    assert attr.semantic.resolved_entity == "x0"
    assert attr.semantic.resolved_path == ["x0", "age"]


def test_quantifier_attribute_receives_symbolic_entity():
    source = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    forall => age <= 30
    """

    ast = _build_and_validate(source)

    root = ast.body[0].rule.assertion.root
    comparison = _collect_comparisons(root)[0]
    attr = comparison.left

    semantic = _semantic(attr)

    assert semantic.resolved_entity == "_x"
    assert semantic.resolved_path == ["_x", "age"]


def test_nested_logic_attributes_receive_semantic_annotations():
    source = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 => (x0.age <= 30 OR x0.income >= 1000) AND x0.score <= 1
    """

    ast = _build_and_validate(source)

    root = ast.body[0].rule.assertion.root
    comparisons = _collect_comparisons(root)

    resolved = {
        cmp.left.feature: _semantic(cmp.left).resolved_entity
        for cmp in comparisons
    }

    assert resolved == {
        "age": "x0",
        "income": "x0",
        "score": "x0",
    }