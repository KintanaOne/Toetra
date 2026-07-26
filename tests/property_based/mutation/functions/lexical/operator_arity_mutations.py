"""
Operator arity violation mutations.

Goal:
- break binary operator structure
- create valid-looking but invalid AST shapes
"""

from __future__ import annotations

import random
import re

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

OPS = [
    "==",
    "!=",
    "~",
    "->",
    "<=",
    ">=",
]


@mutation(
    name="remove_operand",
    layer=Layer.STRING,
    nature=Nature.DELETION,
    strategy=Strategy.CORRUPTED,
    domain=Domain.STRUCTURAL,
    severity=0.8,
    contract=MutationContract(
        cst=PreservationLevel.PARTIAL,
        ast=PreservationLevel.NONE,
        typing=PreservationLevel.NONE,
        semantics=PreservationLevel.NONE,
    ),
)
def remove_operand(text: str) -> str:

    return re.sub(
        r"(==|!=|<=|>=|->|~)\s*\w+",
        r"\1",
        text,
    )


@mutation(
    name="duplicate_operator",
    layer=Layer.STRING,
    nature=Nature.CORRUPTION,
    strategy=Strategy.CORRUPTED,
    domain=Domain.STRUCTURAL,
    severity=0.9,
    contract=MutationContract(
        cst=PreservationLevel.NONE,
        ast=PreservationLevel.NONE,
        typing=PreservationLevel.NONE,
        semantics=PreservationLevel.NONE,
    ),
)
def duplicate_operator(text: str) -> str:

    return re.sub(
        r"(==|!=|<=|>=|->|~)",
        r"\1\1",
        text,
    )


@mutation(
    name="operator_shuffle",
    layer=Layer.STRING,
    nature=Nature.SUBSTITUTION,
    strategy=Strategy.MUTATED,
    domain=Domain.LOGICAL,
    severity=0.6,
    contract=MutationContract(
        cst=PreservationLevel.FULL,
        ast=PreservationLevel.FULL,
        typing=PreservationLevel.PARTIAL,
        semantics=PreservationLevel.NONE,
    ),
)
def operator_shuffle(text: str) -> str:

    return re.sub(
        r"(==|!=|<=|>=|->|~)",
        lambda _: random.choice(OPS),
        text,
    )
