import pytest
from hypothesis import given, settings, HealthCheck

from dsl.parser.parser import parse_forml_code
from dsl.builder.program import parse_program
from dsl.semantic.runtime.tracer import ValidationTracer
from dsl.semantic.core.validator import FORMLValidator
from dsl.parser.errors import ParserError

from test.hypothesis.mutations.ast.semantic import apply_semantic_mutations
from test.hypothesis.strategies.valid.program_string import valid_string_program


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
    cst = parse_forml_code(program)

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
    validator = FORMLValidator()
    tracer = ValidationTracer(enabled=False)

    with pytest.raises(ParserError):
        validator.validate(mutated_ast, tracer=tracer)
