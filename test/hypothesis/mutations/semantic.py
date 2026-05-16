"""
Semantic mutations (AST level).

These mutations operate on FORML AST nodes and
modify logical structure without breaking syntax.
"""

import random
from copy import deepcopy

from dsl.builder.program import ProgramNode
from dsl.builder.assertion import ImplicationNode


# =========================================================
# MUTATIONS
# =========================================================

def break_implication(ast: ProgramNode) -> ProgramNode:
    """
    Swap left and right sides of implications.

    A -> B becomes B -> A
    """

    mutated = deepcopy(ast)

    for p in ast.body:

        assertion = p.rule.assertion.root

        if isinstance(assertion, ImplicationNode):

            assertion.left, assertion.right = (
                assertion.right,
                assertion.left,
            )

    return mutated


def invalidate_property_type(ast: ProgramNode) -> ProgramNode:
    """
    Inject invalid property type into AST.
    """

    mutated = deepcopy(ast)

    for p in mutated.body:

        if hasattr(p, "type") and random.random() < 0.3:
            p.type = "INVALID_TYPE"

    return mutated


def remove_neighborhood(ast: ProgramNode) -> ProgramNode:
    """
    Corrupt semantic constraint nodes.
    """

    mutated = deepcopy(ast)

    for p in mutated.body:

        expr = p.rule.scope

        if hasattr(expr, "neighborhood"):
            expr.neighborhood = None

    return mutated


# =========================================================
# REGISTRY
# =========================================================

SEMANTIC_MUTATIONS = [
    break_implication,
    invalidate_property_type,
    remove_neighborhood,
]


# =========================================================
# ENGINE
# =========================================================

def apply_semantic_mutations(ast: ProgramNode, n: int) -> ProgramNode:
    """
    Apply N semantic mutations on AST.
    """

    mutated = ast

    for _ in range(n):
        mutation = random.choice(SEMANTIC_MUTATIONS)
        mutated = mutation(mutated)

    return mutated