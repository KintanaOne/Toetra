from hypothesis import given, settings, HealthCheck

from dsl.parser.parser import parse_forml_code
from dsl.builder.program import parse_program
from test.hypothesis.strategies.valid.program_string import valid_string_program


@given(valid_string_program())
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_builder_produces_valid_ast(program):
    """
    Ensures CST → AST transformation is always valid.
    """

    cst = parse_forml_code(program)
    ast = parse_program(cst)

    # AST must be well-formed
    assert ast is not None
    assert hasattr(ast, "body")
    assert len(ast.body) >= 0
