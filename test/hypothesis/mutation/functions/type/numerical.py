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

from copy import deepcopy

from dsl.ast.nodes.assertion import ComparisonNode
from dsl.builder.program import ProgramNode
from dsl.ast.nodes.primitives import ConstantNode

from test.hypothesis.mutation.functions.base import (
    MutationLayer,
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
    layer=MutationLayer.NUMERICAL,
    nature=MutationNature.PERTURBATION,
    severity=MutationSeverity.HIGH,
    severity_score=0.8,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=True,
    preserves_typing=True,
    preserves_semantic_equivalence=False,
    preserves_valid_cst=True,
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
    layer=MutationLayer.NUMERICAL,
    nature=MutationNature.SUBSTITUTION,
    severity=MutationSeverity.MEDIUM,
    severity_score=0.6,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=True,
    preserves_typing=True,
    preserves_semantic_equivalence=False,
    preserves_valid_cst=True,
)
def invert_numeric_sign(ast: ProgramNode) -> ProgramNode:
    """
    Invert numeric values.
    """

    mutated = deepcopy(ast)

    for p in mutated.body:

        root = p.rule.assertion.root

        assert isinstance(root, ComparisonNode)

        val = root.right.value
        assert isinstance(val, (int, float))

        if isinstance(root.right, ConstantNode):
            root.right.value = -val

    return mutated


NUMERICAL_MUTATIONS = [
    explode_constants,
    invert_numeric_sign,
]
