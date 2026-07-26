"""
Reserved keyword misuse mutations.

Goal:
- break grammar by injecting keywords
- misuse reserved words
"""

from __future__ import annotations

import random

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
from tests.property_based.mutation.functions.lexical.base_helpers import (
    KEYWORDS,
    replace_identifier,
)


@mutation(
    name="replace_random_identifier",
    layer=Layer.STRING,
    nature=Nature.SUBSTITUTION,
    strategy=Strategy.MUTATED,
    domain=Domain.STRUCTURAL,
    severity=0.5,
    contract=MutationContract(
        cst=PreservationLevel.FULL,
        ast=PreservationLevel.PARTIAL,
        typing=PreservationLevel.PARTIAL,
        semantics=PreservationLevel.NONE,
    ),
)
def replace_random_identifier(program: str) -> str:
    """
    Replace a random LHS identifier in assignments with a random token.
    """

    replacement_pool = [
        "foo",
        "bar",
        "baz",
        "qux",
        "var",
        "temp",
    ]

    replacement = random.choice(replacement_pool)

    return replace_identifier(program, replacement)


@mutation(
    name="keyword_as_identifier",
    layer=Layer.STRING,
    nature=Nature.SUBSTITUTION,
    strategy=Strategy.MUTATED,
    domain=Domain.STRUCTURAL,
    severity=0.5,
    contract=MutationContract(
        cst=PreservationLevel.FULL,
        ast=PreservationLevel.PARTIAL,
        typing=PreservationLevel.PARTIAL,
        semantics=PreservationLevel.NONE,
    ),
)
def keyword_as_identifier(text: str) -> str:
    kw = random.choice(KEYWORDS)

    # replace ONLY ONE identifier
    return replace_identifier(text, kw)


@mutation(
    name="keyword_duplication",
    layer=Layer.STRING,
    nature=Nature.CORRUPTION,
    strategy=Strategy.CORRUPTED,
    domain=Domain.STRUCTURAL,
    severity=0.8,
    contract=MutationContract(
        cst=PreservationLevel.NONE,
        ast=PreservationLevel.NONE,
        typing=PreservationLevel.NONE,
        semantics=PreservationLevel.NONE,
    ),
)
def keyword_duplication(text: str) -> str:

    kw = random.choice(KEYWORDS)

    return text.replace(
        kw,
        kw + " " + kw,
        1,
    )


@mutation(
    name="keyword_injection",
    layer=Layer.STRING,
    nature=Nature.INSERTION,
    strategy=Strategy.CORRUPTED,
    domain=Domain.STRUCTURAL,
    severity=0.8,
    contract=MutationContract(
        cst=PreservationLevel.NONE,
        ast=PreservationLevel.NONE,
        typing=PreservationLevel.NONE,
        semantics=PreservationLevel.NONE,
    ),
)
def keyword_injection(text: str) -> str:
    kw = random.choice(KEYWORDS)
    i = random.randint(0, len(text))
    return text[:i] + f" {kw} " + text[i:]
