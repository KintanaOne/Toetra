from hypothesis import strategies as st
from .primitives import identifiers
from .values import values

logic_ops = st.sampled_from(["==", "!=", "<", "<=", ">", ">="])


@st.composite
def logic_expr(draw):
    attr = draw(identifiers)
    op = draw(logic_ops)
    val = draw(values)

    return f"{attr} {op} {val}"


@st.composite
def assertion(draw):
    left = draw(logic_expr())

    if draw(st.booleans()):
        right = draw(logic_expr())
        return f"{left} -> {right}"

    return left