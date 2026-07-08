# test/hypothesis/mutations/cst/parse.py

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
    nature=MutationNature.SUBSTITUTION,
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
def corrupt_tree_data(
    tree: Tree,
) -> Tree:
    """
    Replace rule name with random invalid one.
    """

    mutated = deepcopy(tree)

    queue = [mutated]

    while queue:

        current = queue.pop()

        if isinstance(current, Tree):

            if random.random() < 0.3:
                current.data = "corrupted_rule"

            queue.extend(child for child in current.children if isinstance(child, Tree))

    return mutated


PARSE_MUTATIONS = [
    corrupt_tree_data,
]
