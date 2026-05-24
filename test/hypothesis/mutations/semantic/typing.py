# test/hypothesis/mutations/semantic/typing_semantic.py

"""
Semantic typing mismatch mutations.

GOAL:
    Corrupt semantic typing assumptions.

ROLE IN FORML:
    - stress type analyzers
    - validate semantic typing
    - test incompatible property semantics

CHARACTERISTICS:
    ✔ AST valid
    ✔ syntax valid
    ❌ semantic typing corrupted
"""

from __future__ import annotations

import random
from copy import deepcopy

from dsl.builder.program import ProgramNode

from dsl.language.vocabulary.properties import (
    EnumProperty,
)

from test.hypothesis.mutations.base import (
    mutation,
    MutationLayer,
    MutationNature,
    MutationSeverity,
    MutationImpact,
    PipelineStage,
)


# =========================================================
# MUTATION 1 : invalidate property semantics
# =========================================================


@mutation(
    layer=MutationLayer.SEMANTIC,
    nature=MutationNature.SUBSTITUTION,
    severity=MutationSeverity.HIGH,
    severity_score=0.85,
    impact={MutationImpact.AST_INVALID},
    expected_failures={
        PipelineStage.SEMANTIC_ANALYSIS,
        PipelineStage.TYPE_CHECKING,
    },
    preserves_valid_cst=True,
    preserves_valid_ast=True,
    preserves_typing=False,
    preserves_semantic_equivalence=False,
)
def invalidate_property_semantic(
    ast: ProgramNode,
) -> ProgramNode:
    """
    Replace semantic property type.
    """

    mutated = deepcopy(ast)

    properties = list(EnumProperty)

    for property_node in mutated.body:

        current = property_node.type

        candidates = [
            p
            for p in properties
            if p != current
        ]

        if candidates:
            property_node.type = random.choice(
                candidates
            )

    return mutated


TYPING_MUTATIONS = [
    invalidate_property_semantic,
]