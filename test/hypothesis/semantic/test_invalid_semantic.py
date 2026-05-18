from hypothesis import given
import pytest

from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code
from dsl.semantic.core.validator import FORMLValidator
from dsl.semantic.runtime.tracer import ValidationTracer
from test.hypothesis.mutations.semantic import apply_semantic_mutations
from test.hypothesis.strategies.valid.program_valid import valid_program


@given(valid_program())
def test_semantic_mutations(program):

    cst = parse_forml_code(program)
    ast = parse_program(cst)

    mutated = apply_semantic_mutations(ast)
    tracer = ValidationTracer(enabled=True)
    validator = FORMLValidator()
    validator.validate(mutated, tracer=tracer)

    with pytest.raises(Exception):
        validator.validate(mutated, tracer=tracer)
