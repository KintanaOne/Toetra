# test/hypothesis/mutations/semantic/relational.py

"""
Semantic relational inconsistency mutations.

GOAL:
    Break semantic relationships between properties.

ROLE IN Toetra:
    - stress semantic ordering
    - validate dependency assumptions
    - test relational robustness

CHARACTERISTICS:
    ✔ AST valid
    ✔ syntax valid
    ✔ typing preserved
    ❌ semantic relationships corrupted
"""

from __future__ import annotations

import random
from copy import deepcopy

from toetra._compiler.builder.program import ProgramNode

from test.hypothesis.mutation.functions.base import (
    mutation,
    MutationLayer,
    MutationNature,
    MutationSeverity,
    MutationImpact,
    PipelineStage,
)

# =========================================================
# MUTATION 1 : reverse property order
# =========================================================


@mutation(
    layer=MutationLayer.SEMANTIC,
    nature=MutationNature.REORDERING,
    severity=MutationSeverity.HIGH,
    severity_score=0.70,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={
        PipelineStage.SEMANTIC_ANALYSIS,
    },
    preserves_valid_cst=True,
    preserves_valid_ast=True,
    preserves_typing=True,
    preserves_semantic_equivalence=False,
)
def reverse_property_order(
    ast: ProgramNode,
) -> ProgramNode:
    """
    Reverse semantic ordering of properties.
    """

    mutated = deepcopy(ast)

    if hasattr(mutated, "body"):
        mutated.body.reverse()

    return mutated


# =========================================================
# MUTATION 2 : shuffle properties
# =========================================================


@mutation(
    layer=MutationLayer.SEMANTIC,
    nature=MutationNature.REORDERING,
    severity=MutationSeverity.MEDIUM,
    severity_score=0.60,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={
        PipelineStage.SEMANTIC_ANALYSIS,
    },
    preserves_valid_cst=True,
    preserves_valid_ast=True,
    preserves_typing=True,
    preserves_semantic_equivalence=False,
)
def shuffle_properties(
    ast: ProgramNode,
) -> ProgramNode:
    """
    Shuffle property ordering.
    """

    mutated = deepcopy(ast)

    if hasattr(mutated, "body"):
        random.shuffle(mutated.body)

    return mutated


RELATIONAL_MUTATIONS = [
    reverse_property_order,
    shuffle_properties,
]
