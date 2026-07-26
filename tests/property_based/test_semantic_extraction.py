from hypothesis import given
import pytest

from toetra._compiler.builder.program import parse_program
from toetra._compiler.parser.parser import parse_toetra_code
from tests.property_based.strategies.valid.program_string import valid_string_program

pytestmark = pytest.mark.wip


@given(valid_string_program())
def test_semantic_extraction(prog):
    ast = parse_toetra_code(prog)
    d = parse_program(ast)

    assert d.header.model is not None
    assert d.header.target is not None
