# dsl/language/tools/constants.py

"""
Central registry of grammar constants used in Lark generation.
All static header definitions and shared mappings live here.
"""

from dsl.language.vocabulary.problems import official_problems
from dsl.language.vocabulary.properties import official_properties
from dsl.language.vocabulary.quantifiers import official_quantifiers
from dsl.language.vocabulary.functions import official_functions
from dsl.language.vocabulary.backends import official_backends
from dsl.language.vocabulary.metrics import official_metrics
from dsl.language.vocabulary.operators import (
    official_logic_operators,
    official_comparaison_operations,
)

# =========================
# RAW DICTIONARIES
# =========================

OFFICIAL_MAPS = {
    "problems": official_problems,
    "properties": official_properties,
    "quantifiers": official_quantifiers,
    "functions": official_functions,
    "backends": official_backends,
    "metrics": official_metrics,
    "logic_operations": official_logic_operators,
    "comparison_operators": official_comparaison_operations,
}

# protected_words volontairement exclu du header rules


# =========================
# HEADER BLOCK GENERATION
# =========================


def format_rule_block(title: str, items: dict) -> list[str]:
    """Convert dictionary into Lark rule list."""
    return (
        [f"# === {title.upper()} ==="] + [f"{k} : {v}" for k, v in items.items()] + [""]
    )


def build_header() -> list[str]:
    """Build full Lark header section."""
    header = [
        "%import common.WS",
        "%import common.WS_INLINE",
        "%import common.NEWLINE",
        "%import common.ESCAPED_STRING",
        "%import common.NUMBER",
        "%import common.DIGIT",
        "%import common.CNAME -> IDENTIFIER",
        "%ignore WS_INLINE",
        "",
        "# === COMMENTS ===",
        "COMMENT_LINE: /#[^\\n]*/",
        "COMMENT_BLOCK: /'''(.|\\n)*?'''/",
        "%ignore COMMENT_LINE",
        "%ignore COMMENT_BLOCK",
        "%ignore NEWLINE",
        "",
    ]

    for name, mapping in OFFICIAL_MAPS.items():
        header += format_rule_block(name, mapping)

    header += [
        "# === TOKENS ===",
        "PAIRWISE.2 : /[A-Za-z][A-Za-z0-9_]*\\s*~\\s*[A-Za-z][A-Za-z0-9_']*/",
        'PROPERTY_IMPLY : "=>"',
        "",
    ]

    return header
