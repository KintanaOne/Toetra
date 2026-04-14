from hypothesis import given

from forml.ast.queries import get_program_dict
from forml.parser.parser import parse_forml_code
from test.hypothesis.strategies.program import program


@given(program())
def test_semantic_extraction(prog):
    ast = parse_forml_code(prog)
    d = get_program_dict(ast)

    assert d["model"] is not None
    assert d["target"] is not None