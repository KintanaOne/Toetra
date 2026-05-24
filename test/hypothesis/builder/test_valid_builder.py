from hypothesis import given
import pytest

from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code

from test.hypothesis.settings import DEFAULT_SETTINGS
from test.hypothesis.strategies.valid.program_string import valid_string_program

pytestmark = pytest.mark.wip


@DEFAULT_SETTINGS
@given(valid_string_program())
def test_builder_accepts_valid_programs(program):

    cst = parse_forml_code(program)
    ast = parse_program(cst)

    assert ast is not None
