"""
Encoding-level corruption mutations.

Goal:
- simulate broken UTF-8 / binary noise
"""

import random
from token import ENCODING
from .base_helpers import inject_noise, random_char_noise

def encoding_corruption(text: str) -> str:
    return inject_noise(text, "\udcff")


def binary_noise(text: str) -> str:
    noise = "".join(random_char_noise() for _ in range(3))
    return inject_noise(text, noise)


ENCODING_MUTATIONS = [
    encoding_corruption,
    binary_noise
]