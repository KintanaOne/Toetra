from hypothesis import given
import pytest
from test.hypothesis.settings import DEFAULT_SETTINGS
from test.hypothesis.strategies.program import program

from dsl.parser.parser import parse_forml_code

@given(program())
def test_parse_deterministic(prog):
    ast1 = parse_forml_code(prog)
    ast2 = parse_forml_code(prog)

    assert ast1 == ast2