"""
Adversarial logical mutations (AST layer)

Goal:
- inject logical contradictions
- create semantic instability
- stress reasoning and validation layers
"""

from __future__ import annotations

import random

from copy import deepcopy

from tests.property_based.mutation.decorators.mutation import mutation

from tests.property_based.mutation.metadata.contract import (
    MutationContract,
    PreservationLevel,
)
from tests.property_based.mutation.metadata.enums import (
    Domain,
    Layer,
    Nature,
    Strategy,
)

from toetra._compiler.ast.nodes.assertion import AndNode, OrNode, NotNode

# =========================================================
# 1. TAUTOLOGY INJECTION
# =========================================================


@mutation(
    name="inject_tautology",
    layer=Layer.AST,
    nature=Nature.CORRUPTION,
    strategy=Strategy.MUTATED,
    domain=Domain.LOGICAL,
    severity=0.9,
    contract=MutationContract(
        cst=PreservationLevel.FULL,
        ast=PreservationLevel.FULL,
        typing=PreservationLevel.FULL,
        semantics=PreservationLevel.NONE,
    ),
)
def inject_tautology(ast):

    root = deepcopy(ast)

    return OrNode(
        operands=[
            root,
            NotNode(operand=deepcopy(root)),
        ],
    )


# =========================================================
# 2. NEGATION CHAOS
# =========================================================


@mutation(
    name="nest_negations",
    layer=Layer.AST,
    nature=Nature.CORRUPTION,
    strategy=Strategy.MUTATED,
    domain=Domain.LOGICAL,
    severity=0.6,
    contract=MutationContract(
        cst=PreservationLevel.FULL,
        ast=PreservationLevel.FULL,
        typing=PreservationLevel.FULL,
        semantics=PreservationLevel.PARTIAL,
    ),
)
def nest_negations(ast):

    root = deepcopy(ast)
    depth = random.randint(2, 6)

    for _ in range(depth):
        root = NotNode(operand=root)

    return root


# =========================================================
# 3. CONTRADICTION INJECTION
# =========================================================


@mutation(
    name="inject_contradiction",
    layer=Layer.AST,
    nature=Nature.CORRUPTION,
    strategy=Strategy.CORRUPTED,
    domain=Domain.LOGICAL,
    severity=0.95,
    contract=MutationContract(
        cst=PreservationLevel.FULL,
        ast=PreservationLevel.FULL,
        typing=PreservationLevel.FULL,
        semantics=PreservationLevel.NONE,
    ),
)
def inject_contradiction(ast):

    root = deepcopy(ast)

    return AndNode(
        operands=[
            root,
            NotNode(operand=deepcopy(root)),
        ],
    )
