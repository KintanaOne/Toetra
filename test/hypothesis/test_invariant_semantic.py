from hypothesis import given

from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code
from test.hypothesis.strategies.program import program


@given(program())
def test_semantic_roundtrip(prog):
    ast1 = parse_forml_code(prog)
    obj1 = parse_program(ast1)

    # reparse même programme
    ast2 = parse_forml_code(prog)
    obj2 = parse_program(ast2)

    assert obj1 == obj2


@given(program())
def test_program_has_valid_structure(prog):
    ast = parse_forml_code(prog)
    d = parse_program(ast)

    assert d.model is not None
    assert d.target is not None
    assert len(d.properties) >= 1