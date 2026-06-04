# test/hypothesis/mutations/semantic/redundancy.py

"""
Semantic redundancy mutations.

GOAL:
    Inject semantically redundant logic.

ROLE IN FORML:
    - stress simplifiers
    - test redundancy handling
    - validate semantic normalization

CHARACTERISTICS:
    ✔ AST valid
    ✔ syntax valid
    ✔ typing preserved
    ❌ semantic signal degraded
"""

from __future__ import annotations

from copy import deepcopy

from dsl.builder.program import ProgramNode

from dsl.ast.nodes.assertion import (
    OrNode,
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
# MUTATION 1 : tautological redundancy
# =========================================================


@mutation(
    layer=MutationLayer.SEMANTIC,
    nature=MutationNature.DUPLICATION,
    severity=MutationSeverity.MEDIUM,
    severity_score=0.55,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={
        PipelineStage.SEMANTIC_ANALYSIS,
    },
    preserves_valid_cst=True,
    preserves_valid_ast=True,
    preserves_typing=True,
    preserves_semantic_equivalence=False,
)
def inject_tautological_redundancy(
    ast: ProgramNode,
) -> ProgramNode:
    """
    Inject:
        A OR NOT(A)
    """

    mutated = deepcopy(ast)

    for property_node in mutated.body:

        root = deepcopy(
            property_node.rule.assertion.root
        )

        tautology = OrNode(
            operands=[
                root,
                NotNode(
                    operand=deepcopy(root)
                ),
            ]
        )

        property_node.rule.assertion.root = tautology

    return mutated


REDUNDANCY_MUTATIONS = [
    inject_tautological_redundancy,
]