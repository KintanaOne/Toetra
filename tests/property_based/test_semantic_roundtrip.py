from hypothesis import given
import pytest

from toetra._compiler.builder.program import parse_program
from toetra._compiler.parser.parser import parse_toetra_code
from tests.property_based.strategies.valid.program_string import valid_string_program

pytestmark = pytest.mark.wip


@given(valid_string_program())
def test_semantic_roundtrip(prog):
    ast1 = parse_toetra_code(prog)
    obj1 = parse_program(ast1)

    # reparse même programme
    ast2 = parse_toetra_code(prog)
    obj2 = parse_program(ast2)

    assert obj1 == obj2
