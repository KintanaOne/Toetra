# test/hypothesis/mutations/cst/tokens.py

from __future__ import annotations

import random
from copy import deepcopy

from lark import Tree, Token

from test.hypothesis.mutation.functions.base import (
    mutation,
    MutationLayer,
    MutationNature,
    MutationSeverity,
    MutationImpact,
    PipelineStage,
)

INVALID_TOKEN_TYPES = [
    "INVALID",
    "CORRUPTED",
    "UNKNOWN",
]


@mutation(
    layer=MutationLayer.LEXICAL,
    nature=MutationNature.CORRUPTION,
    severity=MutationSeverity.HIGH,
    severity_score=0.85,
    impact={MutationImpact.CST_INVALID},
    expected_failures={
        PipelineStage.PARSING,
    },
    preserves_valid_cst=False,
    preserves_valid_ast=False,
    preserves_typing=False,
    preserves_semantic_equivalence=False,
)
def corrupt_token_type(
    tree: Tree,
) -> Tree:
    """
    Replace token type with invalid type.
    """

    mutated = deepcopy(tree)

    queue = [mutated]

    while queue:

        current = queue.pop()

        if not isinstance(current, Tree):
            continue

        for i, child in enumerate(current.children):

            if isinstance(child, Token):

                if random.random() < 0.3:

                    current.children[i] = Token(
                        random.choice(INVALID_TOKEN_TYPES),
                        child.value,
                    )

            elif isinstance(child, Tree):
                queue.append(child)

    return mutated


@mutation(
    layer=MutationLayer.LEXICAL,
    nature=MutationNature.CORRUPTION,
    severity=MutationSeverity.MEDIUM,
    severity_score=0.6,
    impact={MutationImpact.CST_INVALID},
    expected_failures={
        PipelineStage.PARSING,
    },
    preserves_valid_cst=False,
    preserves_valid_ast=False,
    preserves_typing=False,
    preserves_semantic_equivalence=False,
)
def corrupt_token_value(
    tree: Tree,
) -> Tree:
    """
    Replace token value with garbage.
    """

    mutated = deepcopy(tree)

    queue = [mutated]

    while queue:

        current = queue.pop()

        if not isinstance(current, Tree):
            continue

        for i, child in enumerate(current.children):

            if isinstance(child, Token):

                if random.random() < 0.3:

                    current.children[i] = Token(
                        child.type,
                        "@@@CORRUPTED@@@",
                    )

            elif isinstance(child, Tree):
                queue.append(child)

    return mutated


TOKENS_MUTATIONS = [
    corrupt_token_type,
    corrupt_token_value,
]
