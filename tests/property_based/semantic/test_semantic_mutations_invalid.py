import pytest
from hypothesis import given, settings, HealthCheck

from toetra._compiler.parser.parser import parse_toetra_code
from toetra._compiler.builder.program import parse_program
from toetra._compiler.semantic.runtime.tracer import ValidationTracer
from toetra._compiler.semantic.core.validator import ToetraValidator
from toetra._compiler.semantic.errors.errors import SemanticError

from tests.property_based.mutations.ast.semantic import apply_semantic_mutations
from tests.property_based.strategies.valid.program_string import valid_string_program


@given(valid_string_program())
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_semantic_mutations_must_fail_validation(program):
    """
    Property-based test:
    Semantic mutations must break program validity.

    This ensures mutation operators are meaningful.
    """

    # ---------------------------
    # Step 1: Parse to CST
    # ---------------------------
    cst = parse_toetra_code(program)

    # ---------------------------
    # Step 2: Build AST
    # ---------------------------
    ast = parse_program(cst)

    # ---------------------------
    # Step 3: Apply semantic mutations
    # ---------------------------
    mutated_ast = apply_semantic_mutations(ast)

    # ---------------------------
    # Step 4: Validate mutated AST
    # Must fail semantic validation
    # ---------------------------
    validator = ToetraValidator()
    tracer = ValidationTracer(enabled=False)

    with pytest.raises(SemanticError):
        validator.validate(mutated_ast, tracer=tracer)
