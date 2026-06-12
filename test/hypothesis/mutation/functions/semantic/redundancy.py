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

from test.hypothesis.mutation.decorators.mutation import mutation

from test.hypothesis.mutation.functions.semantic.helper.engine import SemanticConstraintEngine
from test.hypothesis.mutation.functions.semantic.helper.extractor import SemanticConstraintExtractor
from test.hypothesis.mutation.functions.semantic.helper.rebuilder import SemanticASTRebuilder
from test.hypothesis.mutation.metadata.contract import MutationContract, PreservationLevel
from test.hypothesis.mutation.metadata.enums import (
    Domain,
    Layer,
    Nature,
    Strategy,
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

@mutation(
    name="semantic.inject_impossible_constraint",
    layer=Layer.AST,
    nature=Nature.CORRUPTION,
    strategy=Strategy.CORRUPTED,
    domain=Domain.LOGICAL,
    severity=0.55,
    contract=MutationContract(
        cst=PreservationLevel.FULL,
        ast=PreservationLevel.FULL,
        typing=PreservationLevel.FULL,
        semantics=PreservationLevel.NONE,
    ),
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
