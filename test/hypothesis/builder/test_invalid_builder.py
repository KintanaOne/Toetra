from hypothesis import given
import pytest

from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code
from test.hypothesis.strategies.invalid.program import apply_lexical_mutations
from test.hypothesis.strategies.valid.program_valid import valid_program

pytestmark = pytest.mark.wip


@given(valid_program())
def test_builder_rejects_invalid_structure(program):

    mutated = apply_lexical_mutations(program)

    with pytest.raises(Exception):
        cst = parse_forml_code(mutated)
        parse_program(cst)
