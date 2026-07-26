"""
Logical negation mutations (Toetra CORE)

GOAL:
    Manipulate negation structure in logical AST.

ROLE:
    - test logical inversion robustness
    - validate normalization layers
    - stress semantic equivalence detection
"""

from __future__ import annotations

from copy import deepcopy

from test.hypothesis.mutation.decorators.mutation import mutation

from test.hypothesis.mutation.metadata.contract import (
    MutationContract,
    PreservationLevel,
)
from test.hypothesis.mutation.metadata.enums import Layer, Nature, Strategy, Domain

from toetra._compiler.builder.assertion import NotNode

# =========================================================
# CONTRACTS
# =========================================================

FULL_SEMANTIC_PRESERVE = MutationContract(
    cst=PreservationLevel.FULL,
    ast=PreservationLevel.FULL,
    typing=PreservationLevel.FULL,
    semantics=PreservationLevel.FULL,
)

PARTIAL_SEMANTIC_BREAK = MutationContract(
    cst=PreservationLevel.FULL,
    ast=PreservationLevel.FULL,
    typing=PreservationLevel.FULL,
    semantics=PreservationLevel.PARTIAL,
)

FULL_SEMANTIC_BREAK = MutationContract(
    cst=PreservationLevel.FULL,
    ast=PreservationLevel.FULL,
    typing=PreservationLevel.FULL,
    semantics=PreservationLevel.NONE,
)


# =========================================================
# 1. NEGATE ASSERTION
# =========================================================


@mutation(
    name="negate_assertion",
    layer=Layer.AST,
    nature=Nature.SUBSTITUTION,
    strategy=Strategy.MUTATED,
    domain=Domain.LOGICAL,
    severity=0.8,
    contract=FULL_SEMANTIC_BREAK,
)
def negate_assertion(ast):

    mutated = deepcopy(ast)

    for p in mutated.body:

        root = p.rule.assertion.root

        p.rule.assertion.root = NotNode(operand=root)

    return mutated


# =========================================================
# 2. REMOVE NEGATION (NORMALIZATION STEP)
# =========================================================


@mutation(
    name="remove_negation",
    layer=Layer.AST,
    nature=Nature.DELETION,
    strategy=Strategy.VALID,
    domain=Domain.LOGICAL,
    severity=0.5,
    contract=PARTIAL_SEMANTIC_BREAK,
)
def remove_negation(ast):

    mutated = deepcopy(ast)

    def _unwrap(node):
        if isinstance(node, NotNode):
            return node.operand
        return node

    for p in mutated.body:
        p.rule.assertion.root = _unwrap(p.rule.assertion.root)

    return mutated


# =========================================================
# 3. DOUBLE NEGATION (SEMANTIC NO-OP)
# =========================================================


@mutation(
    name="inject_double_negation",
    layer=Layer.AST,
    nature=Nature.INSERTION,
    strategy=Strategy.VALID,
    domain=Domain.LOGICAL,
    severity=0.1,
    contract=FULL_SEMANTIC_PRESERVE,
)
def inject_double_negation(ast):

    mutated = deepcopy(ast)

    for p in mutated.body:

        root = deepcopy(p.rule.assertion.root)

        p.rule.assertion.root = NotNode(operand=NotNode(operand=root))

    return mutated
