from hypothesis import given
import pytest

from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code
from test.hypothesis.strategies.valid.program_valid import valid_program

pytestmark = pytest.mark.wip

@given(valid_program())
def test_semantic_extraction(prog):
    ast = parse_forml_code(prog)
    d = parse_program(ast)

    assert d.header.model is not None
    assert d.header.target is not None