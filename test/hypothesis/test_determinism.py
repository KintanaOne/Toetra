from hypothesis import given
import pytest
from test.hypothesis.strategies.valid.program_string import valid_string_program

from dsl.parser.parser import parse_forml_code

pytestmark = pytest.mark.wip


@given(valid_string_program())
def test_parse_deterministic(prog):
    ast1 = parse_forml_code(prog)
    ast2 = parse_forml_code(prog)

    assert ast1 == ast2
