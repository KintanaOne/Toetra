import random
from hypothesis import strategies as st

from test.hypothesis.mutations.semantic.causality import CAUSALITY_MUTATIONS
from test.hypothesis.mutations.semantic.constraints import CONSTRAINT_MUTATIONS
from test.hypothesis.mutations.semantic.context import CONTEXT_MUTATIONS
from test.hypothesis.mutations.semantic.contradiction import CONTRADICTION_MUTATIONS
from test.hypothesis.mutations.semantic.redundancy import REDUNDANCY_MUTATIONS
from test.hypothesis.mutations.semantic.relationnal import RELATIONAL_MUTATIONS
from test.hypothesis.mutations.semantic.scope import SCOPE_MUTATIONS
from test.hypothesis.mutations.semantic.typing import TYPING_MUTATIONS


INVALID_SEMANTIC_MUTATIONS = \
    CAUSALITY_MUTATIONS + \
    CONSTRAINT_MUTATIONS + \
    CONTEXT_MUTATIONS + \
    CONTRADICTION_MUTATIONS + \
    REDUNDANCY_MUTATIONS + \
    RELATIONAL_MUTATIONS + \
    SCOPE_MUTATIONS + \
    TYPING_MUTATIONS
    

def apply_invalid_semantic(ast, mutation_count: int = 1):
    mutated = ast

    for _ in range(mutation_count):
        mutation_fn = random.choice(INVALID_SEMANTIC_MUTATIONS)
        mutated = mutation_fn(mutated)

    return 


@st.composite
def invalid_logic_program(draw, base_ast):
    ast = draw(base_ast)

    mutation_count = draw(st.integers(min_value=1, max_value=3))

    if draw(st.booleans()):
        mutation_count *= 2

    return apply_invalid_semantic(ast, mutation_count)