from hypothesis import strategies as st
from .primitives import identifiers, escaped_strings


@st.composite
def model_declaration(draw):
    path = draw(escaped_strings)
    return f"model := {path}"


@st.composite
def target_declaration(draw):
    target = draw(identifiers)
    return f"target := {target}"


@st.composite
def header(draw):
    model = draw(model_declaration())
    target = draw(target_declaration())

    return f"{model}\n{target}"