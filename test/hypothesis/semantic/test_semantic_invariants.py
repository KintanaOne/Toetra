from hypothesis import given, settings, HealthCheck

from dsl.parser.parser import parse_toetra_code
from dsl.builder.program import parse_program
from dsl.semantic.core.validator import ToetraValidator
from dsl.semantic.runtime.tracer import ValidationTracer
from test.hypothesis.strategies.valid.program_string import valid_string_program


@given(valid_string_program())
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_semantic_invariants_hold(program):
    """
    Ensures that valid programs preserve semantic invariants
    after parsing and validation.
    """

    # Parse pipeline
    cst = parse_toetra_code(program)
    ast = parse_program(cst)

    validator = ToetraValidator()
    tracer = ValidationTracer(enabled=False)

    # Should NOT raise
    result = validator.validate(ast, tracer=tracer)

    # Must be deterministic success
    assert result is True
