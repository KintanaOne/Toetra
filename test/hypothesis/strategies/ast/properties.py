from hypothesis import strategies as st
from .logic import assertion
from ..primitives.args import args
from ..primitives.primitives import identifiers

property_types = st.sampled_from([
    "ROBUSTNESS", "STABILITY", "FAIRNESS",
    "MONOTONICITY", "BOUND", "LOGIC"
])

metrics = st.sampled_from(["L1", "L2", "Linf"])


@st.composite
def neighborhood(draw):
    metric = draw(metrics)
    arg_str = draw(args())
    return f"in neighborhood({metric}, {arg_str})"


@st.composite
def domain(draw):
    domain_name = draw(identifiers)
    values = draw(st.lists(identifiers, min_size=1))
    values_str = ", ".join(f'"{v}"' for v in values)
    return f"with {domain_name}({values_str})"


@st.composite
def at_expr(draw):
    x = draw(identifiers)
    return f"at {x}"


@st.composite
def check_at_expr(draw):
    x = draw(identifiers)
    return f"check_at {x}"


@st.composite
def pairwise_expr(draw):
    x = draw(identifiers)
    x2 = f"{x}'"
    neigh = draw(neighborhood())
    return f"{x} ~ {x2} {neigh}"   # FIX IMPORTANT


@st.composite
def property_expr(draw):
    return draw(st.one_of(
        st.just("forall"),
        pairwise_expr()
    ))


@st.composite
def property(draw):
    ptype = draw(property_types)
    expr = draw(property_expr())
    ass = draw(assertion())

    return f"[{ptype}]: {expr} => {ass}"


backends = st.sampled_from(["z3", "Z3", "eran", "ERAN"])


@st.composite
def abstractor(draw):
    backend = draw(backends)

    if draw(st.booleans()):
        arg_str = draw(args())
        return f"using {backend}({arg_str})"

    return f"using {backend}"


@st.composite
def property_section(draw):
    prop = draw(property())

    if draw(st.booleans()):
        abs_ = draw(abstractor())
        return f"{prop} {abs_}"

    return prop