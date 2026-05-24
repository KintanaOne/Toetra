"""
Reserved keyword misuse mutations.

Goal:
- break grammar by injecting keywords in invalid positions
"""

import random

KEYWORDS = [
    "forall",
    "exists",
    "using",
    "in",
    "with",
    "check_at",
]

def keyword_as_identifier(text: str) -> str:
    kw = random.choice(KEYWORDS)
    return text.replace("A", kw)


def keyword_duplication(text: str) -> str:
    kw = random.choice(KEYWORDS)
    return text.replace(kw, kw + kw)


def keyword_injection(text: str) -> str:
    kw = random.choice(KEYWORDS)
    i = random.randint(0, len(text))
    return text[:i] + f" {kw} " + text[i:]


RESERVED_KEYWORD_MUTATIONS = [
    keyword_as_identifier,
    keyword_duplication,
    keyword_injection,
]