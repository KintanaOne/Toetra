# test/hypothesis/mutations/cst/syntax.py

from __future__ import annotations

import random
from copy import deepcopy

from lark import Tree, Token

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
    nature=MutationNature.DELETION,
    severity=MutationSeverity.HIGH,
    severity_score=0.75,
    impact={MutationImpact.CST_INVALID},
    expected_failures={
        PipelineStage.PARSING,
    },
    preserves_valid_cst=False,
    preserves_valid_ast=False,
    preserves_typing=False,
    preserves_semantic_equivalence=False,
)
def remove_random_token(
    tree: Tree,
) -> Tree:
    """
    Remove random token from CST.
    """

    mutated = deepcopy(tree)

    queue = [mutated]

    while queue:

        current = queue.pop()

        if not isinstance(current, Tree):
            continue

        token_indices = [
            i
            for i, child in enumerate(current.children)
            if isinstance(child, Token)
        ]

        if token_indices and random.random() < 0.3:

            idx = random.choice(token_indices)
            current.children.pop(idx)

        for child in current.children:

            if isinstance(child, Tree):
                queue.append(child)

    return mutated


SYNTAX_MUTATIONS = [
    remove_random_token,
]
