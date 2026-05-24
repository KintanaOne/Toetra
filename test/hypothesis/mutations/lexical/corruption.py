import random
import re
from turtle import st

from test.hypothesis.mutations.base import MutationImpact, MutationLayer, MutationNature, MutationSeverity, PipelineStage, mutation


IDENTIFIER_PATTERN = r"\b[A-Za-z_][A-Za-z0-9_]*\b"

# =========================================================
# INVALID TOKEN MUTATIONS
# =========================================================


RESERVED_KEYWORDS = {
    "model",
    "target",
    "forall",
    "exists",
    "using",
    "neighborhood",
    "in",
    "with"
}

UNICODE_CONFUSABLES = {
    "A": "Α",  # Greek Alpha
    "B": "Β",  # Greek Beta
    "E": "Ε",
    "O": "Ο",
    "a": "а",  # Cyrillic
    "e": "е",
    "o": "о",
}


ZERO_WIDTH_CHARS = [
    "\u200b",  # zero-width space
    "\u200c",
    "\u200d",
]

# =========================================================
# IDENTIFIER MUTATIONS
# =========================================================

def find_valid_identifiers(program: str):
    """
    Find non-reserved identifiers in source code.
    """

    return [
        m
        for m in re.finditer(IDENTIFIER_PATTERN, program)
        if m.group(0) not in RESERVED_KEYWORDS
    ]

@mutation(
    layer=MutationLayer.LEXICAL,
    nature=MutationNature.DELETION,
    severity=MutationSeverity.MEDIUM,
    severity_score=0.4,
    impact={MutationImpact.CST_INVALID},
    expected_failures={PipelineStage.CST_VALIDATION},
    preserves_valid_ast=False,
    preserves_typing=False,
    preserves_semantic_equivalence=False,
    preserves_valid_cst=False
)
def replace_random_identifier(program: str) -> str:
    """
    Replace one valid identifier.
    """

    replacement = random.choice(["foo", "bar", "baz", "qux", "var", "temp"])

    matches = find_valid_identifiers(program)

    if not matches:
        return program

    match = random.choice(matches)

    start, end = match.span()

    return (
        program[:start]
        + replacement
        + program[end:]
    )

# =========================================================
# INVALID CHARACTER MUTATIONS
# =========================================================

@mutation(
    layer=MutationLayer.LEXICAL,
    nature=MutationNature.CORRUPTION,
    severity=MutationSeverity.HIGH,
    severity_score=0.75,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={
        PipelineStage.PARSING,
        PipelineStage.SEMANTIC_ANALYSIS,
    },
    preserves_valid_ast=False,
    preserves_typing=False,
    preserves_semantic_equivalence=False,
    preserves_valid_cst=False
)
def inject_unicode_confusable(program: str) -> str:

    candidates = [
        c for c in UNICODE_CONFUSABLES
        if c in program
    ]

    if not candidates:
        return program

    original = random.choice(candidates)

    return program.replace(
        original,
        UNICODE_CONFUSABLES[original],
        1,
    )

@mutation(
    layer=MutationLayer.LEXICAL,
    nature=MutationNature.CORRUPTION,
    severity=MutationSeverity.HIGH,
    severity_score=0.75,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={
        PipelineStage.PARSING,
        PipelineStage.SEMANTIC_ANALYSIS,
    },
    preserves_valid_ast=False,
    preserves_typing=False,
    preserves_semantic_equivalence=False,
    preserves_valid_cst=False
)
def inject_zero_width(program: str) -> str:

    pos = random.randint(0, len(program))

    zw = random.choice(ZERO_WIDTH_CHARS)

    return (
        program[:pos]
        + zw
        + program[pos:]
    )

@mutation(
    layer=MutationLayer.LEXICAL,
    nature=MutationNature.DELETION,
    severity=MutationSeverity.LOW,
    severity_score=0.4,
    impact={MutationImpact.CST_INVALID},
    expected_failures={PipelineStage.CST_VALIDATION},
    preserves_valid_ast=False,
    preserves_typing=False,
    preserves_semantic_equivalence=False,
    preserves_valid_cst=False
)
def remove_random_character(program: str) -> str:
    """
    Remove one random character.
    """

    if len(program) <= 1:
        return program

    idx = random.randint(0, len(program) - 1)

    return program[:idx] + program[idx + 1 :]


@mutation(
    layer=MutationLayer.LEXICAL,
    nature=MutationNature.CORRUPTION,
    severity=MutationSeverity.HIGH,
    severity_score=0.7,
    impact={MutationImpact.CST_INVALID},
    expected_failures={PipelineStage.CST_VALIDATION},
    preserves_valid_ast=False,
    preserves_typing=False,
    preserves_semantic_equivalence=False,
    preserves_valid_cst=False
)
def inject_noise(program: str) -> str:
    """
    Inject random noise into the DSL text.
    """

    noises = [
        "@@@",
        "???",
        "#!#",
        "::",
        ">>",
        "<<",
    ]

    idx = random.randint(0, len(program))

    noise = random.choice(noises)

    return program[:idx] + noise + program[idx:]


@mutation(
    layer=MutationLayer.LEXICAL,
    nature=MutationNature.CORRUPTION,
    severity=MutationSeverity.HIGH,
    severity_score=0.75,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={
        PipelineStage.PARSING,
        PipelineStage.SEMANTIC_ANALYSIS,
    },
    preserves_valid_ast=False,
    preserves_typing=False,
    preserves_semantic_equivalence=False,
    preserves_valid_cst=False
)
def corrupt_keyword(program: str) -> str:
    """
    Corrupt important DSL keywords.
    """

    replacements = {
        "model": "mod3l",
        "target": "targ3t",
        "using": "us1ng",
        "forall": "for_all",
        "neighborhood": "neighbor",
    }

    mutated = program

    for original, corrupted in replacements.items():

        if original in mutated:
            return mutated.replace(original, corrupted, 1)

    return mutated


@mutation(
    layer=MutationLayer.STRUCTURAL,
    nature=MutationNature.REORDERING,    
    severity=MutationSeverity.MEDIUM,
    severity_score=0.5,
    impact={MutationImpact.CST_INVALID},
    expected_failures={PipelineStage.CST_VALIDATION},
    preserves_valid_ast=False,
    preserves_typing=False,
    preserves_semantic_equivalence=False,
    preserves_valid_cst=False
)
def shuffle_lines(program: str) -> str:
    """
    Shuffle lines order.
    """

    lines = program.split("\n")

    if len(lines) <= 1:
        return program

    random.shuffle(lines)

    return "\n".join(lines)

CORRUPTION_MUTATIONS = [
    replace_random_identifier,
    inject_zero_width,
    inject_noise,
    inject_unicode_confusable,
    remove_random_character,
    corrupt_keyword,
    shuffle_lines,
]