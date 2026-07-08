# test/hypothesis/mutations/cst/tree.py

from __future__ import annotations

import random
from copy import deepcopy

from lark import Tree

from test.hypothesis.mutation.functions.base import (
    mutation,
    MutationLayer,
    MutationNature,
    MutationSeverity,
    MutationImpact,
    PipelineStage,
)


@mutation(
    layer=MutationLayer.STRUCTURAL,
    nature=MutationNature.DUPLICATION,
    severity=MutationSeverity.HIGH,
    severity_score=0.8,
    impact={MutationImpact.CST_INVALID},
    expected_failures={
        PipelineStage.AST_BUILDING,
    },
    preserves_valid_cst=False,
    preserves_valid_ast=False,
    preserves_typing=False,
    preserves_semantic_equivalence=False,
)
def duplicate_random_subtree(
    tree: Tree,
) -> Tree:
    """
    Duplicate random subtree.
    """

    mutated = deepcopy(tree)

    candidates = [child for child in mutated.children if isinstance(child, Tree)]

    if candidates:

        subtree = deepcopy(random.choice(candidates))

        mutated.children.append(subtree)

    return mutated


@mutation(
    layer=MutationLayer.STRUCTURAL,
    nature=MutationNature.REORDERING,
    severity=MutationSeverity.MEDIUM,
    severity_score=0.55,
    impact={MutationImpact.CST_INVALID},
    expected_failures={
        PipelineStage.AST_BUILDING,
    },
    preserves_valid_cst=False,
    preserves_valid_ast=False,
    preserves_typing=False,
    preserves_semantic_equivalence=False,
)
def reverse_tree_children(
    tree: Tree,
) -> Tree:
    """
    Reverse subtree ordering.
    """

    mutated = deepcopy(tree)

    mutated.children.reverse()

    return mutated


TREE_MUTATIONS = [
    duplicate_random_subtree,
    reverse_tree_children,
]
