from hypothesis import given
import pytest

from dsl.builder.program import parse_program
from dsl.parser.parser import parse_toetra_code
from test.hypothesis.strategies.valid.program_string import valid_string_program

pytestmark = pytest.mark.wip


@given(valid_string_program())
def test_semantic_extraction(prog):
    ast = parse_toetra_code(prog)
    d = parse_program(ast)

    assert d.header.model is not None
    assert d.header.target is not None
