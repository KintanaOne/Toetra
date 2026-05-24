"""
Unicode-based lexical corruption.
Breaks tokenizer assumptions and normalization layers.
"""

import random
from .base_helpers import inject_noise

UNICODE_POOL = [
    "𝔄", "𝔅", "𝒜", "𝓐",
    "Ω", "Σ", "Δ",
    "∑", "∫", "∞",
    "\u200b", "\u200d",  # zero-width
    "�",
]

def unicode_injection(text: str) -> str:
    return inject_noise(text, random.choice(UNICODE_POOL))


def unicode_identifier_break(text: str) -> str:
    return text.replace("A", "A" + random.choice(UNICODE_POOL))


UNICODE_MUTATIONS = [
    unicode_injection,
    unicode_identifier_break,
]