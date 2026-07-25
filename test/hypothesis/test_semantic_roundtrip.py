from hypothesis import given
import pytest

from dsl.builder.program import parse_program
from dsl.parser.parser import parse_toetra_code
from test.hypothesis.strategies.valid.program_string import valid_string_program

pytestmark = pytest.mark.wip


@given(valid_string_program())
def test_semantic_roundtrip(prog):
    ast1 = parse_toetra_code(prog)
    obj1 = parse_program(ast1)

    # reparse même programme
    ast2 = parse_toetra_code(prog)
    obj2 = parse_program(ast2)

    assert obj1 == obj2
