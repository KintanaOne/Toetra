# test/hypothesis/mutations/cst/invalid_cst.py

"""
Invalid syntactic mutation entrypoint.

This module composes all syntactic corruption strategies:

- grammar corruption
- parse corruption
- syntax corruption
- token corruption
- tree corruption

GOAL:
    Stress parser robustness and AST builder resilience.

PIPELINE LEVEL:
    TEXT
      ↓
    TOKENS
      ↓
    CST / ParseTree
      ↓
    AST BUILDING

These mutations operate ONLY on Lark CST structures.
"""

from __future__ import annotations

import random

from hypothesis import strategies as st

from lark import Tree

from test.hypothesis.mutations.syntactic.grammar import GRAMMAR_MUTATIONS
from test.hypothesis.mutations.syntactic.parse import PARSE_MUTATIONS
from test.hypothesis.mutations.syntactic.syntax import SYNTAX_MUTATIONS
from test.hypothesis.mutations.syntactic.tokens import TOKENS_MUTATIONS
from test.hypothesis.mutations.syntactic.tree import TREE_MUTATIONS

# =========================================================
# Registry
# =========================================================

INVALID_SYNTACTIC_MUTATIONS = \
    GRAMMAR_MUTATIONS + \
    PARSE_MUTATIONS + \
    SYNTAX_MUTATIONS + \
    TOKENS_MUTATIONS + \
    TREE_MUTATIONS

# =========================================================
# Core mutation engine
# =========================================================


def apply_invalid_syntactic(
    cst: Tree,
    mutation_count: int = 1,
) -> Tree:
    """
    Apply N random CST mutations.
    """

    mutated = cst

    for _ in range(mutation_count):

        mutation_fn = random.choice(
            INVALID_SYNTACTIC_MUTATIONS
        )

        mutated = mutation_fn(mutated)

    return mutated


# =========================================================
# Hypothesis strategy
# =========================================================


@st.composite
def invalid_syntactic_program(
    draw,
    base_program,
) -> Tree:
    """
    Generate an invalid FORML syntactic structure.

    INPUT:
        Valid ParseTree strategy.

    OUTPUT:
        Corrupted CST / ParseTree.
    """

    program = draw(base_program)

    mutation_count = draw(
        st.integers(
            min_value=1,
            max_value=3,
        )
    )

    # heavy corruption mode
    if draw(st.booleans()):

        mutation_count *= 2

    return apply_invalid_syntactic(
        program,
        mutation_count,
    )

