import random
from hypothesis import strategies as st

from test.hypothesis.mutations.logical.adversarial import ADVERSARIAL_MUTATIONS
from test.hypothesis.mutations.logical.boolean import BOOLEAN_MUTATIONS
from test.hypothesis.mutations.logical.implication import IMPLICATION_MUTATIONS
from test.hypothesis.mutations.logical.negation import NEGATION_MUTATIONS
from test.hypothesis.mutations.logical.contradiction import CONTRADICTION_MUTATIONS


INVALID_LOGICAL_MUTATIONS = \
    ADVERSARIAL_MUTATIONS + \
    BOOLEAN_MUTATIONS + \
    CONTRADICTION_MUTATIONS + \
    IMPLICATION_MUTATIONS + \
    NEGATION_MUTATIONS
    

def apply_invalid_logic(ast, mutation_count: int = 1):
    mutated = ast

    for _ in range(mutation_count):
        mutation_fn = random.choice(INVALID_LOGICAL_MUTATIONS)
        mutated = mutation_fn(mutated)

    return 


@st.composite
def invalid_logic_program(draw, base_ast):
    ast = draw(base_ast)

    mutation_count = draw(st.integers(min_value=1, max_value=3))

    if draw(st.booleans()):
        mutation_count *= 2

    return apply_invalid_logic(ast, mutation_count)