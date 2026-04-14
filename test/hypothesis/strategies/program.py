from hypothesis import strategies as st
from .header import header
from .body import body


@st.composite
def program(draw):
    h = draw(header())
    b = draw(body())

    return f"{h}\n\n{b}"