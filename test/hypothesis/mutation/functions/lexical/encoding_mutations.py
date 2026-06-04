"""
Encoding-level corruption mutations.

Goal:
- simulate broken UTF-8
- simulate binary corruption
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

from .base_helpers import (
    inject_noise,
    random_char_noise,
)

@mutation(
    name="encoding_corruption",
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
def encoding_corruption(text: str) -> str:
    """
    Inject invalid unicode surrogate bytes.
    """
    return inject_noise(text, "\udcff")

@mutation(
    name="binary_noise",
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
def binary_noise(text: str) -> str:
    """
    Inject random binary-like control characters.
    """

    noise = "".join(
        random_char_noise()
        for _ in range(3)
    )

    return inject_noise(
        text,
        noise,
    )