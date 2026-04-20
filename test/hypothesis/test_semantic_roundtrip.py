from hypothesis import given

from previous_forml.ast.queries import get_program_dict
from forml.parser.parser import parse_forml_code
from test.hypothesis.strategies.program import program


@given(program())
def test_semantic_roundtrip(prog):
    ast1 = parse_forml_code(prog)
    dict1 = get_program_dict(ast1)

    # reparse même programme
    ast2 = parse_forml_code(prog)
    dict2 = get_program_dict(ast2)

    assert dict1 == dict2