from hypothesis import strategies as st
from lark import ParseTree

from toetra._compiler.parser.parser import parse_toetra_code
from ..ast.header import header
from ..ast.body import body


@st.composite
def valid_syntactic_program(draw) -> ParseTree:
    h = draw(header())
    b = draw(body())

    program = f"{h}\n\n{b}"
    return parse_toetra_code(program)
