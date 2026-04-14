from hypothesis import strategies as st
from .primitives import identifiers
from .values import values


@st.composite
def arg(draw):
    choice = draw(st.integers(min_value=0, max_value=3))

    if choice == 0:
        key = draw(identifiers)
        val = draw(values)
        return f"{key}={val}"

    elif choice == 1:
        return draw(identifiers)

    else:
        return draw(values)


@st.composite
def args(draw):
    args_list = draw(st.lists(arg(), min_size=1, max_size=3))
    return ", ".join(args_list)