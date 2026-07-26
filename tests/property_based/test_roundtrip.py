from hypothesis import given
import pytest
from tests.property_based.strategies.valid.program_string import valid_string_program

from toetra._compiler.parser.parser import parse_toetra_code
from tests.property_based.utils.serialize import serialize

pytestmark = pytest.mark.wip


@pytest.mark.skip(reason="no serialization implemented yet")
@given(valid_string_program())
def test_roundtrip(program):
    ast1 = parse_toetra_code(program)
    serialized = serialize(ast1)
    ast2 = parse_toetra_code(serialized)

    assert ast1 == ast2
