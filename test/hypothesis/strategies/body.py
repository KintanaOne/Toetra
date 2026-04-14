from hypothesis import strategies as st
from .properties import property_section


@st.composite
def body(draw):
    props = draw(st.lists(property_section(), min_size=1, max_size=3))
    return "\n\n".join(props)