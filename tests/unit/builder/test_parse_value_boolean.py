from toetra._compiler.builder.core.ast_utils import parse_value
from toetra._compiler.builder.core.utils import find_node
from toetra._compiler.parser.parser import parse_toetra_code
from toetra._compiler.semantic.types.enums import EnumDataType


def _first_value_node(source: str):
    cst = parse_toetra_code(source)
    value_node = find_node(cst, "value")

    assert value_node is not None

    return value_node


def test_parse_value_true_boolean_literal():
    source = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 => x0.is_active == true
    """

    node = _first_value_node(source)
    value = parse_value(node)

    assert value.value is True
    assert value.dtype is EnumDataType.BOOL


def test_parse_value_false_boolean_literal():
    source = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    check_at x0 => x0.is_active == false
    """

    node = _first_value_node(source)
    value = parse_value(node)

    assert value.value is False
    assert value.dtype is EnumDataType.BOOL
