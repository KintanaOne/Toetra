"""
Logical contradiction & tautology mutations (Toetra CORE)

GOAL:
    Inject semantic impossibilities into AST structures.

ROLE:
    - stress semantic validation layer
    - detect reasoning instability
    - simulate adversarial logical corruption
"""

from __future__ import annotations

from copy import deepcopy

from test.hypothesis.mutation.decorators.mutation import mutation

from test.hypothesis.mutation.metadata.contract import (
    MutationContract,
    PreservationLevel,
)
from test.hypothesis.mutation.metadata.enums import Layer, Nature, Strategy, Domain

from dsl.builder.assertion import AndNode, OrNode, NotNode

# =========================================================
# SHARED CONTRACTS
# =========================================================

FULL_AST_BUT_SEMANTIC_BREAK = MutationContract(
    cst=PreservationLevel.FULL,
    ast=PreservationLevel.FULL,
    typing=PreservationLevel.FULL,
    semantics=PreservationLevel.NONE,
)

PARTIAL_SEMANTIC_BREAK = MutationContract(
    cst=PreservationLevel.FULL,
    ast=PreservationLevel.FULL,
    typing=PreservationLevel.FULL,
    semantics=PreservationLevel.PARTIAL,
)


# =========================================================
# 1. LOCAL CONTRADICTION
# =========================================================


@mutation(
    name="logical.inject_contradiction",
    layer=Layer.AST,
    nature=Nature.CORRUPTION,
    strategy=Strategy.CORRUPTED,
    domain=Domain.LOGICAL,
    severity=0.95,
    contract=FULL_AST_BUT_SEMANTIC_BREAK,
)
def inject_contradiction(ast):

    mutated = deepcopy(ast)

    for p in mutated.body:

        root = deepcopy(p.rule.assertion.root)

        p.rule.assertion.root = AndNode(
            operands=[
                root,
                NotNode(operand=deepcopy(root)),
            ]
        )

    return mutated


# =========================================================
# 2. TAUTOLOGY INJECTION
# =========================================================


@mutation(
    name="logical.inject_tautology",
    layer=Layer.AST,
    nature=Nature.CORRUPTION,
    strategy=Strategy.CORRUPTED,
    domain=Domain.LOGICAL,
    severity=0.8,
    contract=FULL_AST_BUT_SEMANTIC_BREAK,
)
def inject_logical_tautology(ast):

    mutated = deepcopy(ast)

    for p in mutated.body:

        root = deepcopy(p.rule.assertion.root)

        p.rule.assertion.root = OrNode(
            operands=[
                root,
                NotNode(operand=deepcopy(root)),
            ]
        )

    return mutated


# =========================================================
# 3. GLOBAL CONTRADICTION (semantic-level injection)
# =========================================================


@mutation(
    name="logical.inject_global_contradiction",
    layer=Layer.AST,
    nature=Nature.INSERTION,
    strategy=Strategy.CORRUPTED,
    domain=Domain.LOGICAL,
    severity=0.98,
    contract=FULL_AST_BUT_SEMANTIC_BREAK,
)
def inject_global_contradiction(ast):

    mutated = deepcopy(ast)

    for p in mutated.body:

        root = deepcopy(p.rule.assertion.root)

        contradiction = AndNode(
            operands=[
                root,
                NotNode(operand=deepcopy(root)),
            ]
        )

        p.rule.assertion.root = contradiction

    return mutated
