from copy import deepcopy

from hypothesis import given
import pytest

from toetra._compiler.builder.program import parse_program
from toetra._compiler.parser.parser import parse_toetra_code
from tests.property_based.strategies.invalid.invalid_program import invalid_string_program
from tests.property_based.strategies.valid.program_string import valid_string_program

pytestmark = pytest.mark.wip


@given(invalid_string_program(valid_string_program()))
def test_builder_rejects_invalid_structure(program):

    mutated = deepcopy(program)

    with pytest.raises(Exception):
        cst = parse_toetra_code(mutated)
        parse_program(cst)
