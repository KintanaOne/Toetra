from hypothesis import strategies as st

from toetra._compiler.ast.nodes.program import ProgramNode
from toetra._compiler.builder.program import parse_program
from toetra._compiler.parser.parser import parse_toetra_code
from ..ast.header import header
from ..ast.body import body


@st.composite
def valid_cst_program(draw) -> ProgramNode:
    h = draw(header())
    b = draw(body())

    program = f"{h}\n\n{b}"
    cst = parse_toetra_code(program)
    return parse_program(cst)
