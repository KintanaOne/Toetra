from hypothesis import given
import pytest

from toetra._compiler.builder.program import parse_program
from toetra._compiler.parser.errors import ParserError
from toetra._compiler.parser.parser import parse_toetra_code
from toetra._compiler.semantic.core.validator import ToetraValidator
from toetra._compiler.semantic.runtime.tracer import ValidationTracer
from test.hypothesis.mutations.ast.semantic import apply_semantic_mutations


@given(valid_string())
def test_semantic_mutations_invalid(program):
    """
    Property-based test ensuring that mutated semantic programs
    eventually become invalid and raise ParserError.
    """

    try:
        # Step 1: Parse source program into CST
        cst = parse_toetra_code(program)

        # Step 2: Build AST from CST
        ast = parse_program(cst)

        # Step 3: Apply semantic mutations
        mutated = apply_semantic_mutations(ast)

        # Step 4: Validate mutated AST must fail
        validator = ToetraValidator()
        tracer = ValidationTracer(enabled=False)

        with pytest.raises(ParserError):
            validator.validate(mutated, tracer=tracer)

    except ParserError:
        # If parsing already fails, we skip the case
        # because invalid input is outside mutation scope
        pytest.skip("Invalid generated program skipped")
