"""
Semantic mutations (MEANING LEVEL)

GOAL:
    Modify the meaning of the program while preserving syntax.

ROLE IN FORML:
    - test semantic inference
    - validate domain logic
    - detect silent inconsistencies

CHARACTERISTICS:
    ✔ AST usually valid
    ✔ syntax preserved
    ❌ semantic correctness not guaranteed
"""

import random
from copy import deepcopy

from dsl.ast.nodes.expressions import AtExprNode, PairwiseExprNode
from dsl.builder.assertion import ImplicationNode
from dsl.builder.program import ProgramNode
from dsl.language.vocabulary.properties import EnumProperty

from test.hypothesis.mutations.base import (
    MutationImpact,
    mutation,
    MutationNature,
    MutationSeverity,
    PipelineStage,
)


@mutation(
    nature=MutationNature.LOGICAL,
    severity=MutationSeverity.HIGH,
    severity_score=0.7,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=True,
    preserves_typing=True,
)
def break_implication(ast: ProgramNode) -> ProgramNode:
    """
    Swap implication direction.

    A -> B becomes B -> A
    """

    mutated = deepcopy(ast)

    for p in mutated.body:

        assertion = p.rule.assertion.root

        if isinstance(assertion, ImplicationNode):
            assertion.left, assertion.right = (
                assertion.right,
                assertion.left,
            )

    return mutated


@mutation(
    nature=MutationNature.SEMANTIC,
    severity=MutationSeverity.HIGH,
    severity_score=0.8,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={
        PipelineStage.SEMANTIC_ANALYSIS,
        PipelineStage.TYPE_CHECKING,
    },
    preserves_valid_ast=True,
    preserves_typing=False,
)
def invalidate_property_type(ast: ProgramNode) -> ProgramNode:
    """
    Inject invalid property types into the AST.
    """

    mutated = deepcopy(ast)

    old_type = mutated.body[0].type if mutated.body else None

    for p in mutated.body:

        if hasattr(p, "type") and random.random() < 0.3:
            p.type = random.choice([v for v in list(EnumProperty) if v != old_type])

    return mutated


@mutation(
    nature=MutationNature.STRUCTURAL,
    severity=MutationSeverity.CRITICAL,
    impact={MutationImpact.SEMANTIC_INVALID},
    severity_score=0.95,
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=False,
    preserves_typing=False,
)
def remove_neighborhood(ast: ProgramNode) -> ProgramNode:
    """
    Break neighborhood constraints.

    NOTE:
        This mutation may violate structural invariants.
    """

    mutated = deepcopy(ast)

    for p in mutated.body:

        expr = p.rule.scope

        if isinstance(expr, AtExprNode):
            expr.neighborhood = None

        elif isinstance(expr, PairwiseExprNode):
            object.__setattr__(expr, "neighborhood", None)

    return mutated


SEMANTIC_MUTATIONS = [
    break_implication,
    invalidate_property_type,
    remove_neighborhood,
]


def apply_semantic_mutations(ast: ProgramNode, n: int = 1) -> ProgramNode:
    """
    Apply N semantic mutations.
    """

    mutated = ast

    for _ in range(n):
        mutation_fn = random.choice(SEMANTIC_MUTATIONS)
        mutated = mutation_fn(mutated)

    return mutated
