# test/hypothesis/mutations/semantic/constraints.py

"""
Semantic constraint violation mutations.

GOAL:
    Inject impossible or contradictory semantic constraints.

ROLE IN FORML:
    - stress semantic validators
    - detect contradiction handling
    - validate logical consistency

CHARACTERISTICS:
    ✔ AST valid
    ✔ syntax valid
    ✔ typing preserved
    ❌ semantic consistency broken
"""

from __future__ import annotations

from copy import deepcopy

from dsl.builder.program import ProgramNode

from dsl.ast.nodes.assertion import (
    AndNode,
    NotNode,
)

from test.hypothesis.mutation.functions.base import (
    mutation,
    MutationLayer,
    MutationNature,
    MutationSeverity,
    MutationImpact,
    PipelineStage,
)


# =========================================================
# MUTATION 1 : impossible semantic constraint
# =========================================================


@mutation(
    layer=MutationLayer.SEMANTIC,
    nature=MutationNature.CORRUPTION,
    severity=MutationSeverity.CRITICAL,
    severity_score=1.0,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={
        PipelineStage.SEMANTIC_ANALYSIS,
    },
    preserves_valid_cst=True,
    preserves_valid_ast=True,
    preserves_typing=True,
    preserves_semantic_equivalence=False,
)
def inject_impossible_constraint(
    ast: ProgramNode,
) -> ProgramNode:
    """
    Inject contradiction:
        A becomes A AND NOT(A)
    """

    mutated = deepcopy(ast)

    for property_node in mutated.body:

        root = deepcopy(
            property_node.rule.assertion.root
        )

        contradiction = AndNode(
            operands=[
                root,
                NotNode(
                    operand=deepcopy(root)
                ),
            ]
        )

        property_node.rule.assertion.root = contradiction

    return mutated


CONSTRAINT_MUTATIONS = [
    inject_impossible_constraint,
]