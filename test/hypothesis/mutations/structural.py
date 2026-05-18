"""
Structural mutations (AST LEVEL)

GOAL:
    Modify the structure of the AST.

ROLE IN FORML:
    - test AST builder robustness
    - break structural invariants
    - simulate upstream corruption

CHARACTERISTICS:
    ✔ AST exists
    ❌ semantic validity not guaranteed
    ❌ structural invariants often violated
"""

import random

from dsl.ast.nodes.program import ProgramNode

from test.hypothesis.mutations.base import (
    MutationImpact,
    mutation,
    MutationNature,
    MutationSeverity,
    PipelineStage,
)


@mutation(
    nature=MutationNature.STRUCTURAL,
    severity=MutationSeverity.CRITICAL,
    severity_score=0.9,
    impact={MutationImpact.AST_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS, },
    preserves_valid_ast=False,
    preserves_typing=False,
)
def remove_model(ast: ProgramNode) -> ProgramNode:
    """
    Remove the model declaration from the AST.
    """

    if hasattr(ast, "header"):
        object.__setattr__(ast.header, "model", None)

    return ast


@mutation(
    nature=MutationNature.STRUCTURAL,
    severity=MutationSeverity.CRITICAL,
    severity_score=0.9,
    impact={MutationImpact.AST_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=False,
    preserves_typing=False,
)
def remove_target(ast: ProgramNode) -> ProgramNode:
    """
    Remove the target declaration from the AST.
    """

    if hasattr(ast, "header"):
        object.__setattr__(ast.header, "target", None)

    return ast


@mutation(
    nature=MutationNature.STRUCTURAL,
    severity=MutationSeverity.CATASTROPHIC,
    severity_score=1.0,
    impact={MutationImpact.AST_INVALID},
    expected_failures={PipelineStage.SEMANTIC_ANALYSIS},
    preserves_valid_ast=False,
    preserves_typing=False,
)
def remove_body(ast: ProgramNode) -> ProgramNode:
    """
    Remove the entire program body.

    RESULT:
        - empty AST
        - total loss of semantics
    """

    if hasattr(ast, "body"):
        ast.body = []

    return ast


@mutation(
    nature=MutationNature.STRUCTURAL,
    severity=MutationSeverity.HIGH,
    severity_score=0.7,
    impact={MutationImpact.AST_INVALID},
    expected_failures={
        PipelineStage.AST_BUILDING,
        PipelineStage.SEMANTIC_ANALYSIS,
    },
    preserves_valid_ast=False,
    preserves_typing=False,
)
def reorder_sections(ast: ProgramNode) -> ProgramNode:
    """
    Shuffle top-level AST sections.

    EFFECT:
        - breaks structural consistency
    """

    if not hasattr(ast, "__dict__"):
        return ast

    items = list(vars(ast).items())
    random.shuffle(items)

    for k, v in items:
        setattr(ast, k, v)

    return ast


STRUCTURAL_MUTATIONS = [
    remove_model,
    remove_target,
    remove_body,
    reorder_sections,
]


def apply_structural_mutations(ast: ProgramNode, n: int = 1) -> ProgramNode:
    """
    Apply N structural mutations.
    """

    mutated = ast

    for _ in range(n):
        mutation_fn = random.choice(STRUCTURAL_MUTATIONS)
        mutated = mutation_fn(mutated)

    return mutated