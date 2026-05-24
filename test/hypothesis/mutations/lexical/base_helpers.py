"""
Base helpers for lexical invalid mutation system.

These utilities are shared across all mutation categories.
"""

import random
import re

# -------------------------------------------------
# Regex approximations (adjust to FORML grammar if needed)
# -------------------------------------------------

IDENTIFIER_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
NUMBER_RE = re.compile(r"\b\d+(\.\d+)?\b")
STRING_RE = re.compile(r'"([^"\\]|\\.)*"')
OPERATOR_RE = re.compile(r"(==|!=|<=|>=|->|~|=|\+|-|\*|/)")

# -------------------------------------------------
# Core safe mutation helpers
# -------------------------------------------------

def replace_with_regex(text: str, regex, fn):
    def _repl(match):
        return fn(match.group(0))
    return regex.sub(_repl, text)


def inject_noise(text: str, payload: str) -> str:
    i = random.randint(0, len(text))
    return text[:i] + payload + text[i:]


def random_char_noise():
    return chr(random.randint(0, 31))


def random_ascii_garbage():
    return random.choice(["�", "\x00", "\x1f", "\uffff"])