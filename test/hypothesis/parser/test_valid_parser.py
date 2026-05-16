from hypothesis import given
from test.hypothesis.settings import DEFAULT_SETTINGS
from test.hypothesis.strategies.valid.program_valid import valid_program

from dsl.parser.parser import parse_forml_code


@given(valid_program())
def test_parser_accepts_valid(program):
    cst = parse_forml_code(program)
    assert cst is not None