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
ASSIGNMENT_RE = re.compile(r"(?P<lhs>[A-Za-z_][A-Za-z0-9_]*)\s*=")

KEYWORDS = [
    "forall",
    "exists",
    "using",
    "in",
    "with",
    "check_at",
]

UNICODE_POOL = [
    "𝔄", "𝔅", "𝒜", "𝓐",
    "Ω", "Σ", "Δ",
    "∑", "∫", "∞",
    "\u200b", "\u200d",  # zero-width
    "�",
]
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

def find_identifiers(text: str):
    """
    Return all identifiers appearing on the LHS of assignments.
    """
    return list(ASSIGNMENT_RE.finditer(text))


def replace_identifier(
    text: str,
    replacement: str,
    *,
    replace_all: bool = False
) -> str:
    """
    Replace identifiers defined as LHS of assignments:
        foo = bar

    Args:
        text: input program
        replacement: string to substitute identifiers with
        replace_all: if True replace all identifiers, else only one

    Returns:
        mutated text
    """

    matches = list(ASSIGNMENT_RE.finditer(text))

    if not matches:
        return text

    if replace_all:
        # replace from right to left to avoid offset issues
        for m in reversed(matches):
            start, end = m.span("lhs")
            text = text[:start] + replacement + text[end:]
        return text

    m = random.choice(matches)
    start, end = m.span("lhs")

    return text[:start] + replacement + text[end:]