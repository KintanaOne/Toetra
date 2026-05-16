from hypothesis import given

from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code
from test.hypothesis.strategies.valid.program import program


@given(program())
def test_semantic_extraction(prog):
    ast = parse_forml_code(prog)
    d = parse_program(ast)

    assert d["model"] is not None
    assert d["target"] is not None