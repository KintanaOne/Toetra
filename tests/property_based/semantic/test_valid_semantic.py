from hypothesis import given
import pytest

from toetra._compiler.builder.program import parse_program
from toetra._compiler.parser.parser import parse_toetra_code
from toetra._compiler.semantic.core.validator import ToetraValidator
from toetra._compiler.semantic.runtime.tracer import ValidationTracer
from tests.property_based.strategies.valid.program_string import valid_string_program

pytestmark = pytest.mark.wip


@given(valid_string_program())
def test_semantic_validation(program):

    cst = parse_toetra_code(program)
    ast = parse_program(cst)

    tracer = ValidationTracer(enabled=True)
    validator = ToetraValidator()
    validator.validate(ast, tracer=tracer)
