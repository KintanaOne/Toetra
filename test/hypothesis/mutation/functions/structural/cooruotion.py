"""
Structural corruption mutations

GOAL:
    Introduce invalid AST fields or broken nodes.

ROLE IN FORML:
    - test defensive parsing
    - simulate malformed serialization
"""

import random
from copy import deepcopy

from dsl.ast.nodes.program import ProgramNode
from test.hypothesis.mutation.functions.base import PipelineStage, mutation, MutationLayer, MutationNature, MutationSeverity, MutationImpact


@mutation(
    layer=MutationLayer.STRUCTURAL,
    nature=MutationNature.CORRUPTION,
    severity=MutationSeverity.CRITICAL,
    severity_score=1.0,
    impact={MutationImpact.AST_INVALID},
    expected_failures={PipelineStage.AST_BUILDING, 
                       PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=False,
    preserves_valid_cst=False,
    preserves_typing=False,
)
def inject_none(ast):
    mutated = deepcopy(ast)
    mutated.body.append(None)
    return mutated


@mutation(
    layer=MutationLayer.STRUCTURAL,
    nature=MutationNature.CORRUPTION,
    severity=MutationSeverity.HIGH,
    severity_score=0.8,
    impact={MutationImpact.AST_INVALID},
    expected_failures={PipelineStage.AST_BUILDING,
                       PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=False,
    preserves_valid_cst=False,
    preserves_typing=False,
)
def corrupt_node_type(ast: ProgramNode):
    mutated = deepcopy(ast)

    if mutated.body:
        object.__setattr__(
                mutated.body[0],
                "type",
                "UNKNOWN_TYPE",
            )

    return mutated


CORRUPTION_MUTATIONS = [
    inject_none,
    corrupt_node_type,
]


def apply_corruption(ast, n=1):
    mutated = ast
    for _ in range(n):
        mutated = random.choice(CORRUPTION_MUTATIONS)(mutated)
    return mutated