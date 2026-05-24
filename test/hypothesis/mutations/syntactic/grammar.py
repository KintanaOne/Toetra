# test/hypothesis/mutations/cst/grammar.py

from __future__ import annotations

import random
from copy import deepcopy

from lark import Tree

from test.hypothesis.mutations.base import (
    mutation,
    MutationLayer,
    MutationNature,
    MutationSeverity,
    MutationImpact,
    PipelineStage,
)


@mutation(
    layer=MutationLayer.STRUCTURAL,
    nature=MutationNature.REORDERING,
    severity=MutationSeverity.CRITICAL,
    severity_score=0.95,
    impact={MutationImpact.CST_INVALID},
    expected_failures={
        PipelineStage.PARSING,
        PipelineStage.AST_BUILDING,
    },
    preserves_valid_cst=False,
    preserves_valid_ast=False,
    preserves_typing=False,
    preserves_semantic_equivalence=False,
)
def reorder_grammar_rules(
    tree: Tree,
) -> Tree:
    """
    Randomly reorder grammar children.
    """

    mutated = deepcopy(tree)

    if mutated.children:
        random.shuffle(mutated.children)

    return mutated


@mutation(
    layer=MutationLayer.STRUCTURAL,
    nature=MutationNature.DELETION,
    severity=MutationSeverity.CRITICAL,
    severity_score=1.0,
    impact={MutationImpact.CST_INVALID},
    expected_failures={
        PipelineStage.PARSING,
        PipelineStage.AST_BUILDING,
    },
    preserves_valid_cst=False,
    preserves_valid_ast=False,
    preserves_typing=False,
    preserves_semantic_equivalence=False,
)
def remove_random_subtree(
    tree: Tree,
) -> Tree:
    """
    Remove a random subtree.
    """

    mutated = deepcopy(tree)

    candidates = [
        i
        for i, child in enumerate(mutated.children)
        if isinstance(child, Tree)
    ]

    if candidates:
        idx = random.choice(candidates)
        mutated.children.pop(idx)

    return mutated


GRAMMAR_MUTATIONS = [
    reorder_grammar_rules,
    remove_random_subtree,
]
