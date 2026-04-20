from hypothesis import given

from previous_forml.ast.queries import get_program_dict
from dsl.parser.parser import parse_forml_code
from test.hypothesis.strategies.program import program


@given(program())
def test_semantic_roundtrip(prog):
    ast1 = parse_forml_code(prog)
    dict1 = get_program_dict(ast1)

    # reparse même programme
    ast2 = parse_forml_code(prog)
    dict2 = get_program_dict(ast2)

    assert dict1 == dict2


@given(program())
def test_program_has_valid_structure(prog):
    ast = parse_forml_code(prog)
    d = get_program_dict(ast)

    assert d["model"] is not None
    assert d["target"] is not None
    assert len(d["properties"]) >= 1