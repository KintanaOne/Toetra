from hypothesis import given, settings, HealthCheck

from toetra._compiler.parser.parser import parse_toetra_code
from toetra._compiler.builder.program import parse_program
from tests.property_based.strategies.valid.program_string import valid_string_program


@given(valid_string_program())
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_builder_produces_valid_ast(program):
    """
    Ensures CST → AST transformation is always valid.
    """

    cst = parse_toetra_code(program)
    ast = parse_program(cst)

    # AST must be well-formed
    assert ast is not None
    assert hasattr(ast, "body")
    assert len(ast.body) >= 0
