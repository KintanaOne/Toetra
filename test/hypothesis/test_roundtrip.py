from hypothesis import given
import pytest
from test.hypothesis.settings import DEFAULT_SETTINGS
from test.hypothesis.strategies.valid.program import program

from dsl.parser.parser import parse_forml_code
from test.hypothesis.utils.serialize import serialize

@pytest.mark.skip(reason="no serialization implemented yet")
@given(program())
def test_roundtrip(program):
    ast1 = parse_forml_code(program)
    serialized = serialize(ast1)
    ast2 = parse_forml_code(serialized)

    assert ast1 == ast2