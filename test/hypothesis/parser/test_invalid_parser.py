import pytest
from hypothesis import given
from test.hypothesis.settings import DEFAULT_SETTINGS
from test.hypothesis.strategies.invalid.program import invalid_program

from dsl.parser.parser import parse_forml_code

pytestmark = pytest.mark.wip

@given(invalid_program())
def test_parser_rejects_invalid(program):
    with pytest.raises(Exception):
        parse_forml_code(program)