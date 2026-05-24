import random
from hypothesis import strategies as st

from test.hypothesis.mutations.structural.cooruotion import CORRUPTION_MUTATIONS
from test.hypothesis.mutations.structural.deletion import DELETION_MUTATIONS
from test.hypothesis.mutations.structural.duplication import DUPLICATION_MUTATIONS
from test.hypothesis.mutations.structural.hierarchy import HIERARCHY_MUTATIONS
from test.hypothesis.mutations.structural.invariants import INVARIANTS_MUTATIONS
from test.hypothesis.mutations.structural.ordering import ORDERING_MUTATIONS


INVALID_STRUCTURAL_MUTATIONS = \
    CORRUPTION_MUTATIONS + \
    DELETION_MUTATIONS + \
    DUPLICATION_MUTATIONS + \
    HIERARCHY_MUTATIONS + \
    INVARIANTS_MUTATIONS + \
    ORDERING_MUTATIONS

def apply_invalid_structural(ast, mutation_count: int = 1):
    mutated = ast

    for _ in range(mutation_count):
        mutation_fn = random.choice(INVALID_STRUCTURAL_MUTATIONS)
        mutated = mutation_fn(mutated)

    return 


@st.composite
def invalid_structural_program(draw, base_ast):
    ast = draw(base_ast)

    mutation_count = draw(st.integers(min_value=1, max_value=3))

    if draw(st.booleans()):
        mutation_count *= 2

    return apply_invalid_structural(ast, mutation_count)