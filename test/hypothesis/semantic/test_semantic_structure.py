from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code


@given(valid_programs())
def test_program_has_valid_structure(program):

    cst = parse_forml_code(program)
    ast = parse_program(cst)

    assert ast.header is not None
    assert ast.header.model is not None
    assert ast.header.target is not None

    assert len(ast.body) > 0