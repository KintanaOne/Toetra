"""
Structural ordering mutations

GOAL:
    Break ordering assumptions in AST traversal.

ROLE IN Toetra:
    - test deterministic pipelines
    - break ordering invariants
    - stress semantic aggregation layers

CHARACTERISTICS:
    ✔ AST exists
    ❌ ordering assumptions broken
"""

import random
from copy import deepcopy

from toetra._compiler.ast.nodes.program import ProgramNode
from tests.property_based.mutation.functions.base import (
    mutation,
    MutationLayer,
    MutationNature,
    MutationSeverity,
    MutationImpact,
    PipelineStage,
)


@mutation(
    layer=MutationLayer.STRUCTURAL,
    nature=MutationNature.REORDERING,
    severity=MutationSeverity.HIGH,
    severity_score=0.7,
    impact={MutationImpact.AST_INVALID},
    expected_failures={PipelineStage.AST_BUILDING, PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=False,
    preserves_valid_cst=False,
    preserves_typing=False,
)
def reorder_sections(ast: ProgramNode):
    mutated = deepcopy(ast)

    if hasattr(mutated, "body"):
        random.shuffle(mutated.body)

    return mutated


ORDERING_MUTATIONS = [
    reorder_sections,
]


def apply_ordering(ast: ProgramNode, n: int = 1):
    mutated = ast
    for _ in range(n):
        mutated = random.choice(ORDERING_MUTATIONS)(mutated)
    return mutated
