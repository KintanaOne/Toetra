from hypothesis import strategies as st

from dsl.ast.nodes.program import ProgramNode
from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code
from ..ast.header import header
from ..ast.body import body


@st.composite
def valid_cst_program(draw) -> ProgramNode:
    h = draw(header())
    b = draw(body())

    program = f"{h}\n\n{b}"
    cst = parse_forml_code(program)
    return parse_program(cst)
