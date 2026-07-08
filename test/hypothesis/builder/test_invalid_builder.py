from copy import deepcopy

from hypothesis import given
import pytest

from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code
from test.hypothesis.strategies.invalid.invalid_program import invalid_string_program
from test.hypothesis.strategies.valid.program_string import valid_string_program

pytestmark = pytest.mark.wip


@given(invalid_string_program(valid_string_program()))
def test_builder_rejects_invalid_structure(program):

    mutated = deepcopy(program)

    with pytest.raises(Exception):
        cst = parse_forml_code(mutated)
        parse_program(cst)
