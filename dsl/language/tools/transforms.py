# dsl/language/tools/transforms.py

"""
EBNF → Lark transformation utilities.
"""

import re

# =========================
# RULE CONTEXT DETECTION
# =========================


def is_rule_root(line: str) -> bool:
    """
    Detect if we are at rule root level AFTER assignment conversion.
    """
    return ":" in line and not line.strip().startswith("#")


# =========================
# ASSIGNMENT FIRST (IMPORTANT)
# =========================


def convert_assignment(line: str) -> str:
    """
    Convert EBNF assignment to Lark BEFORE any transformation.
    """
    return re.sub(r"^(\??\w+)\s*=", r"\1 :", line)


# =========================
# BRACKET PROTECTION
# =========================


def protect_brackets(line: str) -> str:
    def repl(match):
        content = match.group(0)
        replacements = {
            '"["': "___BRACKET_OPEN___",
            '"]"': "___BRACKET_CLOSE___",
            '"("': "___PAREN_OPEN___",
            '")"': "___PAREN_CLOSE___",
            '"{"': "___CURLY_OPEN___",
            '"}"': "___CURLY_CLOSE___",
        }
        for k, v in replacements.items():
            content = content.replace(k, v)
        return content

    return re.sub(r'"[^"]*"', repl, line)


def unprotect_brackets(line: str) -> str:
    replacements = {
        "___BRACKET_OPEN___": '"["',
        "___BRACKET_CLOSE___": '"]"',
        "___PAREN_OPEN___": '"("',
        "___PAREN_CLOSE___": '")"',
        "___CURLY_OPEN___": '"{"',
        "___CURLY_CLOSE___": '"}"',
    }
    for k, v in replacements.items():
        line = line.replace(k, v)
    return line


# =========================
# EBNF STRUCTURES
# =========================


def transform_ebnf_brackets(line: str) -> str:
    def repl_curly(match):
        return f"({match.group(1)})*"

    def repl_brackets(match):
        return f"({match.group(1)})?"

    def protect_or_groups(line: str) -> str:
        """
        Ensure OR chains are preserved as atomic blocks.
        """

        def repl(match):
            group = match.group(0)
            return f"( {group} )"

        # match A | B | C pattern
        return re.sub(r"(?:[A-Z_]+\s*\|\s*)+[A-Z_]+", repl, line)

    prev = None
    while prev != line:
        prev = line
        line = re.sub(r"\{([^{}]+)\}", repl_curly, line)
        line = re.sub(r"\[([^\[\]]+)\]", repl_brackets, line)
        line = protect_or_groups(line)

    return line


# =========================
# MAIN RESOLVER (FIXED)
# =========================


def replace_all_sequences(line: str, registry: dict) -> str:
    """
    Replace ?tokens? using registry.

    Adds automatic grouping for:
    - metrics
    - backends
    """

    root = is_rule_root(line)

    WRAP_PAREN = {
        "official_metrics",
        "official_backends",
    }

    def resolve(key: str):
        for group in ["SPECIAL_SEQ", "PRIMITIVE_SEQ", "MISC_SEQ"]:
            if key in registry[group]:
                return registry[group][key], group
        raise KeyError(f"Unknown placeholder: ?{key}?")

    def repl(match):
        key = match.group(1).strip()
        value, group = resolve(key)

        # regex passthrough
        if isinstance(value, str) and value.startswith("/") and value.endswith("/"):
            return value

        value_str = str(value)

        # 🔥 ONLY WRAP SELECTED GROUPS
        if group == "SPECIAL_SEQ" and key in WRAP_PAREN:
            return f"{value_str}"

        # root rule safety (no parentheses globally)
        if root:
            return value_str

        # fallback
        if "|" in value_str:
            return f"( {value_str} )"

        return value_str

    return re.sub(r"\?\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\?", repl, line)


# =========================
# CLEANERS
# =========================


def normalize_whitespace(line: str) -> str:
    parts = re.split(r"(/[^/]+/)", line)  # split regex vs non-regex
    cleaned = []

    for part in parts:
        if part.startswith("/") and part.endswith("/"):
            cleaned.append(part)  # 🔒 untouched regex
        else:
            cleaned.append(re.sub(r"[ \t]+", " ", part))  # only spaces/tabs

    return "".join(cleaned).strip()


def remove_ebnf_commas(line: str) -> str:
    result = []
    in_string = False
    depth = 0

    for char in line:
        if char == '"':
            in_string = not in_string
            result.append(char)
            continue

        if not in_string:
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1

            if char == ",":
                result.append(" ")
                continue

        result.append(char)

    return "".join(result)


# =========================
# PIPELINE SAFETY FOR OR BLOCKS
# =========================


def group_or_blocks(line: str) -> str:
    """
    Force parentheses around OR blocks when they are followed by tokens.
    Fixes Lark ambiguity like:
        A | B "." C
    """

    # pattern: A | B | C "." D  => (A | B | C) "." D
    return re.sub(r"((?:[A-Z_]+\s*\|\s*)+[A-Z_]+)\s*(\.)", r"(\1) \2", line)


# =========================
# NEIGHBORHOOD PRECEDENCE
# =========================


def fix_neighborhood_precedence(line: str) -> str:
    """
    Fix:
    L1 | L2 | LINF ","
    => (L1 | L2 | LINF) ","
    """

    # capture metric block
    return re.sub(
        r"\(\s*metric\s*=\s*\)\?\s*([A-Z0-9_]+)\s*\|\s*([A-Z0-9_]+)\s*\|\s*([A-Z0-9_]+)",
        r'("metric" "=")? (\1 | \2 | \3)',
        line,
    )
