import random
import re

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
    "with",
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
    name="replace_random_identifier",
    layer=Layer.STRING,
    nature=Nature.SUBSTITUTION,
    strategy=Strategy.MUTATED,
    domain=Domain.SEMANTIC,
    severity=0.4,
    contract=MutationContract(
        cst=PreservationLevel.FULL,
        ast=PreservationLevel.PARTIAL,
        typing=PreservationLevel.PARTIAL,
        semantics=PreservationLevel.NONE,
    ),
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

    return program[:start] + replacement + program[end:]


# =========================================================
# INVALID CHARACTER MUTATIONS
# =========================================================


@mutation(
    name="inject_unicode_confusable",
    layer=Layer.STRING,
    nature=Nature.CORRUPTION,
    strategy=Strategy.CORRUPTED,
    domain=Domain.SEMANTIC,
    severity=0.75,
    contract=MutationContract(
        cst=PreservationLevel.NONE,
        ast=PreservationLevel.NONE,
        typing=PreservationLevel.NONE,
        semantics=PreservationLevel.NONE,
    ),
)
def inject_unicode_confusable(program: str) -> str:

    candidates = [c for c in UNICODE_CONFUSABLES if c in program]

    if not candidates:
        return program

    original = random.choice(candidates)

    return program.replace(
        original,
        UNICODE_CONFUSABLES[original],
        1,
    )


@mutation(
    name="inject_zero_width",
    layer=Layer.STRING,
    nature=Nature.CORRUPTION,
    strategy=Strategy.CORRUPTED,
    domain=Domain.STRUCTURAL,
    severity=0.75,
    contract=MutationContract(
        cst=PreservationLevel.NONE,
        ast=PreservationLevel.NONE,
        typing=PreservationLevel.NONE,
        semantics=PreservationLevel.NONE,
    ),
)
def inject_zero_width(program: str) -> str:

    pos = random.randint(0, len(program))

    zw = random.choice(ZERO_WIDTH_CHARS)

    return program[:pos] + zw + program[pos:]


@mutation(
    name="remove_random_character",
    layer=Layer.STRING,
    nature=Nature.CORRUPTION,
    strategy=Strategy.CORRUPTED,
    domain=Domain.STRUCTURAL,
    severity=0.4,
    contract=MutationContract(
        cst=PreservationLevel.PARTIAL,
        ast=PreservationLevel.PARTIAL,
        typing=PreservationLevel.PARTIAL,
        semantics=PreservationLevel.PARTIAL,
    ),
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
    name="inject_noise",
    layer=Layer.STRING,
    nature=Nature.CORRUPTION,
    strategy=Strategy.CORRUPTED,
    domain=Domain.STRUCTURAL,
    severity=0.7,
    contract=MutationContract(
        cst=PreservationLevel.NONE,
        ast=PreservationLevel.NONE,
        typing=PreservationLevel.NONE,
        semantics=PreservationLevel.NONE,
    ),
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
    name="corrupt_keyword",
    layer=Layer.STRING,
    nature=Nature.CORRUPTION,
    strategy=Strategy.CORRUPTED,
    domain=Domain.SEMANTIC,
    severity=0.8,
    contract=MutationContract(
        cst=PreservationLevel.NONE,
        ast=PreservationLevel.NONE,
        typing=PreservationLevel.NONE,
        semantics=PreservationLevel.NONE,
    ),
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
    name="shuffle_lines",
    layer=Layer.STRING,
    nature=Nature.REORDERING,
    strategy=Strategy.CORRUPTED,
    domain=Domain.STRUCTURAL,
    severity=0.5,
    contract=MutationContract(
        cst=PreservationLevel.NONE,
        ast=PreservationLevel.NONE,
        typing=PreservationLevel.NONE,
        semantics=PreservationLevel.NONE,
    ),
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
