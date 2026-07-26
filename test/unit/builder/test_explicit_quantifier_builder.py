import pytest

from toetra._compiler.ast.nodes.expressions import QuantifierExprNode
from toetra._compiler.builder.program import parse_program
from toetra._compiler.parser.parser import parse_toetra_code


@pytest.mark.parametrize(
    ("quantifier", "identifier"),
    [
        ("forall", "x0"),
        ("exists", "candidate"),
        ("∀", "sample"),
        ("∃", "witness"),
    ],
)
def test_builder_preserves_explicit_quantified_identifier(
    quantifier: str,
    identifier: str,
):
    source = f"""
    model := "model.onnx"
    target := MyTarget

    [LOGIC]:
    {quantifier} {identifier} => score >= 0
    """

    program = parse_program(parse_toetra_code(source))
    scope = program.body[0].rule.scope

    assert isinstance(scope, QuantifierExprNode)
    assert scope.quantifier == quantifier
    assert scope.variable == identifier
