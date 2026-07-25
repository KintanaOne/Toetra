"""
Structural duplication mutations

GOAL:
    Introduce redundancy at AST level.

ROLE IN Toetra:
    - stress deduplication logic
    - break uniqueness constraints
"""

import random
from copy import deepcopy

from test.hypothesis.mutation.functions.base import (
    PipelineStage,
    mutation,
    MutationLayer,
    MutationNature,
    MutationSeverity,
    MutationImpact,
)


@mutation(
    layer=MutationLayer.STRUCTURAL,
    nature=MutationNature.DUPLICATION,
    severity=MutationSeverity.MEDIUM,
    severity_score=0.6,
    impact={MutationImpact.AST_INVALID},
    expected_failures={PipelineStage.AST_BUILDING},
    preserves_valid_ast=False,
    preserves_valid_cst=False,
    preserves_typing=False,
)
def duplicate_body(ast):
    mutated = deepcopy(ast)

    if hasattr(mutated, "body") and mutated.body:
        mutated.body = mutated.body + mutated.body

    return mutated


DUPLICATION_MUTATIONS = [
    duplicate_body,
]


def apply_duplication(ast, n=1):
    mutated = ast
    for _ in range(n):
        mutated = random.choice(DUPLICATION_MUTATIONS)(mutated)
    return mutated
