from hypothesis import given
import pytest
from test.hypothesis.strategies.valid.program_valid import valid_program

from dsl.parser.parser import parse_forml_code

pytestmark = pytest.mark.wip


@given(valid_program())
def test_parser_accepts_valid(program):
    cst = parse_forml_code(program)
    assert cst is not None
