"""
Unicode-based lexical corruption.
Breaks tokenizer assumptions and normalization layers.
"""


from __future__ import annotations

import random

from test.hypothesis.mutation.decorators.mutation import mutation

from test.hypothesis.mutation.metadata.contract import (
    MutationContract,
    PreservationLevel,
)

from test.hypothesis.mutation.metadata.enums import (
    Domain,
    Layer,
    Nature,
    Strategy,
)

from .base_helpers import UNICODE_POOL, inject_noise, replace_identifier



@mutation(
    name="unicode_injection",
    layer=Layer.STRING,
    nature=Nature.CORRUPTION,
    strategy=Strategy.CORRUPTED,
    domain=Domain.STRUCTURAL,
    severity=0.85,
    contract=MutationContract(
        cst=PreservationLevel.NONE,
        ast=PreservationLevel.NONE,
        typing=PreservationLevel.NONE,
        semantics=PreservationLevel.NONE,
    ),
)
def unicode_injection(text: str) -> str:
    """
    Injects random unicode artifacts into the program text.
    """

    return inject_noise(
        text,
        random.choice(UNICODE_POOL),
    )


@mutation(
    name="unicode_identifier_break",
    layer=Layer.STRING,
    nature=Nature.SUBSTITUTION,
    strategy=Strategy.CORRUPTED,
    domain=Domain.STRUCTURAL,
    severity=0.7,
    contract=MutationContract(
        cst=PreservationLevel.FULL,
        ast=PreservationLevel.PARTIAL,
        typing=PreservationLevel.PARTIAL,
        semantics=PreservationLevel.NONE,
    ),
)
def unicode_identifier_break(text: str) -> str:
    """
    Break identifiers by injecting unicode artifacts into LHS variables.
    """

    return replace_identifier(
        text,
        replacement=random.choice(UNICODE_POOL),
    )

