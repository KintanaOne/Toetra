from hypothesis import given, settings, HealthCheck

from toetra._compiler.parser.parser import parse_toetra_code
from toetra._compiler.builder.program import parse_program
from toetra._compiler.semantic.core.validator import ToetraValidator
from toetra._compiler.semantic.runtime.tracer import ValidationTracer
from tests.property_based.strategies.valid.program_string import valid_string_program


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
