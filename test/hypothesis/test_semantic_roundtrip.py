from hypothesis import given

from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code
from test.hypothesis.strategies.valid.program import program


@given(program())
def test_semantic_roundtrip(prog):
    ast1 = parse_forml_code(prog)
    obj1 = parse_program(ast1)

    # reparse même programme
    ast2 = parse_forml_code(prog)
    obj2 = parse_program(ast2)

    assert obj1 == obj2