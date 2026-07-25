from dsl.ast.nodes.assertion import ComparisonNode
from dsl.ast.nodes.primitives import TargetRefNode
from dsl.builder.program import parse_program
from dsl.parser.parser import parse_toetra_code
from dsl.semantic.core.validator import ToetraValidator


def test_target_ref_resolves_to_model_target():
    code = """
    model := "model.onnx"
    target := MyTarget

    [BOUND]:
    forall x0 => target <= 10
    """

    program = parse_program(parse_toetra_code(code))

    ToetraValidator().validate(program)

    comparison = program.body[0].rule.assertion.root

    assert isinstance(comparison, ComparisonNode)
    assert isinstance(comparison.left, TargetRefNode)

    semantic = comparison.left.semantic

    assert semantic is not None
    assert semantic.resolved_entity == "_model"
    assert semantic.resolved_path == ["_model", "MyTarget"]
    assert semantic.resolved_type == "model_output"
