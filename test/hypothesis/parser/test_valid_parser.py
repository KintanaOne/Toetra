from hypothesis import given
import pytest
from test.hypothesis.strategies.valid.program_string import valid_string_program

from toetra._compiler.parser.parser import parse_toetra_code

pytestmark = pytest.mark.wip


@given(valid_string_program())
def test_parser_accepts_valid(program):
    cst = parse_toetra_code(program)
    assert cst is not None
