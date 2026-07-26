"""
Structural deletion mutations (AST integrity breaking)

GOAL:
    Remove mandatory or structural components of the AST.

ROLE IN Toetra:
    - test AST robustness
    - break required schema contracts
    - simulate partial compilation / truncation

CHARACTERISTICS:
    ✔ AST may still exist
    ❌ structure often invalid
    ❌ semantic validity broken
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

# ----------------------------
# Delete header parts
# ----------------------------


@mutation(
    layer=MutationLayer.STRUCTURAL,
    nature=MutationNature.DELETION,
    severity=MutationSeverity.CRITICAL,
    severity_score=0.95,
    impact={MutationImpact.AST_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=False,
    preserves_valid_cst=False,
    preserves_typing=False,
)
def remove_model(ast: ProgramNode):
    mutated = deepcopy(ast)
    if hasattr(mutated.header, "model"):
        object.__setattr__(mutated.header, "model", None)
    return mutated


@mutation(
    layer=MutationLayer.STRUCTURAL,
    nature=MutationNature.DELETION,
    severity=MutationSeverity.CRITICAL,
    severity_score=0.95,
    impact={MutationImpact.AST_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=False,
    preserves_valid_cst=False,
    preserves_typing=False,
)
def remove_target(ast: ProgramNode):
    mutated = deepcopy(ast)
    if hasattr(mutated.header, "target"):
        object.__setattr__(mutated.header, "target", None)
    return mutated


@mutation(
    layer=MutationLayer.STRUCTURAL,
    nature=MutationNature.DELETION,
    severity=MutationSeverity.CATASTROPHIC,
    severity_score=1.0,
    impact={MutationImpact.AST_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=False,
    preserves_valid_cst=False,
    preserves_typing=False,
)
def remove_body(ast: ProgramNode):
    mutated = deepcopy(ast)
    mutated.body = []
    return mutated


DELETION_MUTATIONS = [
    remove_model,
    remove_target,
    remove_body,
]


def apply_deletion(ast: ProgramNode, n: int = 1):
    mutated = ast
    for _ in range(n):
        mutated = random.choice(DELETION_MUTATIONS)(mutated)
    return mutated
