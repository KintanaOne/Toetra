from hypothesis import strategies as st
from ..primitives.primitives import identifiers, escaped_strings


# ======================================================================
# REQUIRED PARTS
# ======================================================================

@st.composite
def model_declaration(draw):
    path = draw(escaped_strings)
    return f"model := {path}"


@st.composite
def target_declaration(draw):
    target = draw(identifiers)
    return f"target := {target}"


# ======================================================================
# OPTIONAL PARTS
# ======================================================================

@st.composite
def dataset_declaration(draw):
    path = draw(escaped_strings)
    return f"dataset := {path}"


@st.composite
def variables_declaration(draw):
    vars_list = draw(
        st.lists(identifiers, min_size=1, max_size=5)
    )
    return "variables := " + ", ".join(vars_list)


# ======================================================================
# HEADER COMPOSITION
# ======================================================================

@st.composite
def header(draw):
    model = draw(model_declaration())
    target = draw(target_declaration())

    parts = [model, target]

    # dataset optionnel
    if draw(st.booleans()):
        parts.append(draw(dataset_declaration()))

    # variables optionnel
    # if draw(st.booleans()):
    #     parts.append(draw(variables_declaration()))

    return "\n".join(parts)