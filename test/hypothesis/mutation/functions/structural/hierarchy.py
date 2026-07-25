"""
Structural hierarchy mutations

GOAL:
    Break AST tree hierarchy integrity.

ROLE IN Toetra:
    - test tree traversal robustness
    - break parent/child assumptions
    - simulate malformed AST builders
"""

import random
from copy import deepcopy

from test.hypothesis.mutation.functions.base import (
    mutation,
    MutationLayer,
    MutationNature,
    MutationSeverity,
    MutationImpact,
    PipelineStage,
)


@mutation(
    layer=MutationLayer.STRUCTURAL,
    nature=MutationNature.CORRUPTION,
    severity=MutationSeverity.HIGH,
    severity_score=0.85,
    impact={MutationImpact.AST_INVALID},
    expected_failures={PipelineStage.AST_BUILDING, PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=False,
    preserves_valid_cst=False,
    preserves_typing=False,
)
def flatten_ast(ast):
    mutated = deepcopy(ast)

    if hasattr(mutated, "body"):
        mutated.body = [node for p in mutated.body for node in getattr(p, "body", [p])]

    return mutated


@mutation(
    layer=MutationLayer.STRUCTURAL,
    nature=MutationNature.CORRUPTION,
    severity=MutationSeverity.CRITICAL,
    severity_score=1.0,
    impact={MutationImpact.AST_INVALID},
    expected_failures={PipelineStage.AST_BUILDING, PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=False,
    preserves_valid_cst=False,
    preserves_typing=False,
)
def promote_child_to_root(ast):
    mutated = deepcopy(ast)

    if mutated.body:
        mutated.body = [mutated.body[0]] + mutated.body[1:]

    return mutated


HIERARCHY_MUTATIONS = [
    flatten_ast,
    promote_child_to_root,
]


def apply_hierarchy(ast, n=1):
    mutated = ast
    for _ in range(n):
        mutated = random.choice(HIERARCHY_MUTATIONS)(mutated)
    return mutated
