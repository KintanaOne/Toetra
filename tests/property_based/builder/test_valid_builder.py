from hypothesis import given
import pytest

from toetra._compiler.builder.program import parse_program
from toetra._compiler.parser.parser import parse_toetra_code

from tests.property_based.settings import DEFAULT_SETTINGS
from tests.property_based.strategies.valid.program_string import valid_string_program

pytestmark = pytest.mark.wip


@DEFAULT_SETTINGS
@given(valid_string_program())
def test_builder_accepts_valid_programs(program):

    cst = parse_toetra_code(program)
    ast = parse_program(cst)

    assert ast is not None
