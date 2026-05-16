from hypothesis import given

from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code

from test.hypothesis.settings import DEFAULT_SETTINGS
from test.hypothesis.strategies.valid.program_valid import valid_program


@DEFAULT_SETTINGS
@given(valid_program())
def test_builder_accepts_valid_programs(program):

    cst = parse_forml_code(program)

    ast = parse_program(cst)

    assert ast is not None