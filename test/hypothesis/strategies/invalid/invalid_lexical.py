"""
Invalid lexical mutation entrypoint.

This module composes all lexical failure modes:
- Unicode corruption
- Encoding corruption
- Reserved keyword misuse
- Operator arity violations

Used as first stage in FORML adversarial pipeline.
"""

import random
from turtle import st

from test.hypothesis.mutations.lexical.corruption import CORRUPTION_MUTATIONS
from test.hypothesis.mutations.lexical.encoding_mutations import ENCODING_MUTATIONS
from test.hypothesis.mutations.lexical.operator_arity_mutations import OPERATOR_ARITY_MUTATIONS
from test.hypothesis.mutations.lexical.reserved_keyword_mutations import RESERVED_KEYWORD_MUTATIONS
from test.hypothesis.mutations.lexical.unicode_mutations import UNICODE_MUTATIONS


INVALID_STRING_MUTATIONS = \
    ENCODING_MUTATIONS + \
    CORRUPTION_MUTATIONS + \
    OPERATOR_ARITY_MUTATIONS + \
    RESERVED_KEYWORD_MUTATIONS + \
    UNICODE_MUTATIONS


# =========================================================
# Core mutation engine (lexical only)
# =========================================================

def apply_invalid_lexical(text: str, mutation_count: int = 1) -> str:
    """
    Apply N random lexical mutations.
    """
    mutated = text

    for _ in range(mutation_count):
        mutation = random.choice(INVALID_STRING_MUTATIONS)
        mutated = mutation(mutated)

    return mutated

# =========================================================
# MAIN STRATEGY
# =========================================================


# =========================================================
# Hypothesis strategy
# =========================================================

@st.composite
def invalid_lexical_program(draw, base_program : str) -> str:
    """
    Generate a lexically invalid FORML program.

    Parameters
    ----------
    base_program:
        strategy producing valid FORML programs (string)

    Returns
    -------
    str (invalid FORML program)
    """

    program = draw(base_program)

    # number of mutations (controlled chaos)
    mutation_count = draw(st.integers(min_value=1, max_value=3))

    # optional: probability of "heavy corruption"
    if draw(st.booleans()):
        mutation_count *= 2

    return apply_invalid_lexical(program, mutation_count)