# test/hypothesis/mutations/semantic/causality.py

"""
Semantic causality mutations.

GOAL:
    Break semantic causal relationships.

ROLE IN FORML:
    - stress implication semantics
    - reverse semantic directionality
    - validate causal consistency

CHARACTERISTICS:
    ✔ AST valid
    ✔ syntax valid
    ✔ typing preserved
    ❌ semantic causality corrupted
"""

from __future__ import annotations

from copy import deepcopy

from dsl.builder.program import ProgramNode

from dsl.builder.assertion import (
    ImplicationNode,
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
# MUTATION 1 : reverse causality
# =========================================================


@mutation(
    layer=MutationLayer.SEMANTIC,
    nature=MutationNature.REORDERING,
    severity=MutationSeverity.HIGH,
    severity_score=0.80,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={
        PipelineStage.SEMANTIC_ANALYSIS,
    },
    preserves_valid_cst=True,
    preserves_valid_ast=True,
    preserves_typing=True,
    preserves_semantic_equivalence=False,
)
def reverse_causality(
    ast: ProgramNode,
) -> ProgramNode:
    """
    Reverse implication direction.

    A -> B becomes B -> A
    """

    mutated = deepcopy(ast)

    for property_node in mutated.body:

        root = property_node.rule.assertion.root

        if isinstance(root, ImplicationNode):

            root.left, root.right = (
                root.right,
                root.left,
            )

    return mutated


CAUSALITY_MUTATIONS = [
    reverse_causality,
]