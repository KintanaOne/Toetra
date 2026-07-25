from hypothesis import given
import pytest
from test.hypothesis.strategies.valid.program_string import valid_string_program

from dsl.parser.parser import parse_toetra_code

pytestmark = pytest.mark.wip


@given(valid_string_program())
def test_parse_deterministic(prog):
    ast1 = parse_toetra_code(prog)
    ast2 = parse_toetra_code(prog)

    assert ast1 == ast2
