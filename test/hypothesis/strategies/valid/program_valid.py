from hypothesis import strategies as st
from ..ast.header import header
from ..ast.body import body


@st.composite
def valid_program(draw):
    h = draw(header())
    b = draw(body())

    return f"{h}\n\n{b}"