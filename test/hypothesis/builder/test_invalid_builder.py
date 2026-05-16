from hypothesis import given
import pytest

from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code
from test.hypothesis.strategies.valid.program_valid import valid_program


@given(valid_program())
def test_builder_rejects_invalid_structure(program):

    cst = parse_forml_code(program)

    mutated = mutate_cst(cst)

    with pytest.raises(Exception):
        parse_program(mutated)