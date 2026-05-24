from hypothesis import given
import pytest

from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code
from dsl.semantic.core.validator import FORMLValidator
from dsl.semantic.runtime.tracer import ValidationTracer
from test.hypothesis.strategies.valid.program_string import valid_string_program

pytestmark = pytest.mark.wip


@given(valid_string_program())
def test_semantic_validation(program):

    cst = parse_forml_code(program)
    ast = parse_program(cst)

    tracer = ValidationTracer(enabled=True)
    validator = FORMLValidator()
    validator.validate(ast, tracer=tracer)
