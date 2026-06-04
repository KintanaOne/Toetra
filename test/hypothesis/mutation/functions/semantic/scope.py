# test/hypothesis/mutations/semantic/scope.py

"""
Semantic scope corruption mutations.

GOAL:
    Break semantic scope consistency.

ROLE IN FORML:
    - stress neighborhood validation
    - corrupt semantic domains
    - test scope assumptions

CHARACTERISTICS:
    ✔ AST valid
    ✔ syntax valid
    ❌ semantic scope invalid
"""

from __future__ import annotations

from copy import deepcopy

from dsl.builder.program import ProgramNode

from dsl.ast.nodes.expressions import (
    PairwiseExprNode,
    AtExprNode,
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
# MUTATION 1 : remove neighborhood
# =========================================================


@mutation(
    layer=MutationLayer.SEMANTIC,
    nature=MutationNature.DELETION,
    severity=MutationSeverity.CRITICAL,
    severity_score=0.95,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={
        PipelineStage.SEMANTIC_ANALYSIS,
    },
    preserves_valid_cst=True,
    preserves_valid_ast=False,
    preserves_typing=False,
    preserves_semantic_equivalence=False,
)
def remove_neighborhood(
    ast: ProgramNode,
) -> ProgramNode:
    """
    Remove neighborhood constraints.
    """

    mutated = deepcopy(ast)

    for property_node in mutated.body:

        scope = property_node.rule.scope

        if isinstance(scope, PairwiseExprNode):

            object.__setattr__(
                scope,
                "neighborhood",
                None,
            )

        elif isinstance(scope, AtExprNode):

            scope.neighborhood = None

    return mutated


SCOPE_MUTATIONS = [
    remove_neighborhood,
]