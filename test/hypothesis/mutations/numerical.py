"""
Numerical mutations (VALUE LEVEL)

GOAL:
    Corrupt numeric assumptions in the DSL.

ROLE IN FORML:
    - stress thresholds and constraints
    - break metric-based reasoning
    - test numerical stability of validation pipeline

CHARACTERISTICS:
    ✔ AST valid
    ✔ syntax valid
    ✔ categorical structure preserved
    ❌ numeric meaning corrupted
"""

import random
from copy import deepcopy

from dsl.ast.nodes.assertion import ComparisonNode
from dsl.builder.program import ProgramNode
from dsl.ast.nodes.primitives import ConstantNode

from test.hypothesis.mutations.base import (
    mutation,
    MutationNature,
    MutationSeverity,
    MutationImpact,
    PipelineStage,
)

# =========================================================
# MUTATION 1 : epsilon explosion
# =========================================================


@mutation(
    nature=MutationNature.NUMERICAL,
    severity=MutationSeverity.HIGH,
    severity_score=0.8,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=True,
    preserves_typing=True,
)
def explode_constants(ast: ProgramNode) -> ProgramNode:
    """
    Replace numeric constants with extreme values.
    """

    mutated = deepcopy(ast)

    for p in mutated.body:

        root = p.rule.assertion.root

        assert isinstance(root, ComparisonNode)

        if isinstance(root.right, ConstantNode):
            root.right.value = float("inf")

    return mutated


# =========================================================
# MUTATION 2 : sign inversion
# =========================================================


@mutation(
    nature=MutationNature.NUMERICAL,
    severity=MutationSeverity.MEDIUM,
    severity_score=0.6,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=True,
    preserves_typing=True,
)
def invert_numeric_sign(ast: ProgramNode) -> ProgramNode:
    """
    Invert numeric values.
    """

    mutated = deepcopy(ast)

    for p in mutated.body:

        root = p.rule.assertion.root

        assert isinstance(root, ComparisonNode)
        val = root.right.dtype in {"int", "float"}

        if isinstance(root.right, ConstantNode):
            root.right.value = -val

    return mutated


NUMERICAL_MUTATIONS = [
    explode_constants,
    invert_numeric_sign,
]


def apply_numerical_mutations(ast: ProgramNode, n: int = 1) -> ProgramNode:
    """
    Apply N numerical mutations.
    """

    mutated = ast

    for _ in range(n):
        mutation_fn = random.choice(NUMERICAL_MUTATIONS)
        mutated = mutation_fn(mutated)

    return mutated
