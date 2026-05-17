"""
Multi-layer invalid FORML program generation.

Pipeline:
    valid_program (string)
        ↓
    lexical mutations
        ↓
    CST
        ↓
    structural mutations
        ↓
    AST
        ↓
    semantic mutations

This module generates invalid artifacts across
multiple layers of the FORML pipeline.
"""

import random

from hypothesis.strategies import composite

from dsl.parser.parser import parse_forml_code
from dsl.builder.program import parse_program

from test.hypothesis.strategies.valid.program_valid import valid_program

from test.hypothesis.mutations.lexical import (
    LEXICAL_MUTATIONS,
)

from test.hypothesis.mutations.structural import (
    STRUCTURAL_MUTATIONS,
)

from test.hypothesis.mutations.semantic import (
    SEMANTIC_MUTATIONS,
)


# =========================================================
# GENERIC MUTATION ENGINE
# =========================================================

def mutate(obj, mutation_pool):
    """
    Apply one random mutation from a mutation pool.
    """

    mutation = random.choice(mutation_pool)

    return mutation(obj)


# =========================================================
# LEXICAL LAYER
# =========================================================

def apply_lexical_mutations(
    program: str,
    mutation_count: int,
):
    """
    Apply lexical mutations on DSL text.
    """

    mutated = program

    for _ in range(mutation_count):
        mutated = mutate(mutated, LEXICAL_MUTATIONS)

    return mutated


# =========================================================
# STRUCTURAL LAYER (CST)
# =========================================================

def apply_structural_mutations(
    cst,
    mutation_count: int,
):
    """
    Apply structural mutations on CST.
    """

    mutated = cst

    for _ in range(mutation_count):
        mutated = mutate(mutated, STRUCTURAL_MUTATIONS)

    return mutated


# =========================================================
# SEMANTIC LAYER (AST)
# =========================================================

def apply_semantic_mutations(
    ast,
    mutation_count: int,
):
    """
    Apply semantic mutations on AST.
    """

    mutated = ast

    for _ in range(mutation_count):
        mutated = mutate(mutated, SEMANTIC_MUTATIONS)

    return mutated


# =========================================================
# MAIN STRATEGY
# =========================================================

@composite
def invalid_program(
    draw,
    lexical_ratio: float = 0.4,
    structural_ratio: float = 0.3,
    semantic_ratio: float = 0.3,
    max_mutations: int = 3,
):
    """
    Generate invalid FORML artifacts.

    Ratios determine the probability of applying
    mutations at each pipeline layer.

    Parameters
    ----------
    lexical_ratio:
        Probability of lexical (string) mutations.

    structural_ratio:
        Probability of structural (CST) mutations.

    semantic_ratio:
        Probability of semantic (AST) mutations.

    max_mutations:
        Maximum mutations applied per layer.

    Returns
    -------
    Depending on mutation stage:
        - str
        - CST
        - AST
    """

    # -----------------------------------------------------
    # STEP 1: valid DSL program
    # -----------------------------------------------------

    program = draw(valid_program())

    # -----------------------------------------------------
    # STEP 2: lexical mutations
    # -----------------------------------------------------

    if random.random() < lexical_ratio:

        lexical_mutation_count = random.randint(
            1,
            max_mutations,
        )

        program = apply_lexical_mutations(
            program,
            lexical_mutation_count,
        )

    # -----------------------------------------------------
    # STEP 3: parser
    # -----------------------------------------------------

    try:
        cst = parse_forml_code(program)

    except Exception:
        # lexical corruption successfully broke parser
        return program

    # -----------------------------------------------------
    # STEP 4: structural mutations
    # -----------------------------------------------------

    if random.random() < structural_ratio:

        structural_mutation_count = random.randint(
            1,
            max_mutations,
        )

        cst = apply_structural_mutations(
            cst,
            structural_mutation_count,
        )

    # -----------------------------------------------------
    # STEP 5: builder
    # -----------------------------------------------------

    try:
        ast = parse_program(cst)

    except Exception:
        # structural corruption successfully broke builder
        return cst

    # -----------------------------------------------------
    # STEP 6: semantic mutations
    # -----------------------------------------------------

    if random.random() < semantic_ratio:

        semantic_mutation_count = random.randint(
            1,
            max_mutations,
        )

        ast = apply_semantic_mutations(
            ast,
            semantic_mutation_count,
        )

    # -----------------------------------------------------
    # FINAL OUTPUT
    # -----------------------------------------------------

    return ast