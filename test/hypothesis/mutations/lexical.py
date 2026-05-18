"""
Lexical mutations (STRING level).

These mutations operate directly on raw DSL text.
Their goal is to stress the lexer/parser layer.
"""

import random

from test.hypothesis.mutations.base import (
    MutationImpact,
    MutationNature,
    MutationSeverity,
    PipelineStage,
    mutation,
)


@mutation(
    nature=MutationNature.STRUCTURAL,
    severity=MutationSeverity.MEDIUM,
    severity_score=0.4,
    impact={MutationImpact.PARSING},
    expected_failures={PipelineStage.PARSING},
    preserves_valid_ast=False,
    preserves_typing=False,
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
    nature=MutationNature.STRUCTURAL,
    severity=MutationSeverity.HIGH,
    severity_score=0.7,
    impact={MutationImpact.PARSING},
    expected_failures={PipelineStage.PARSING},
    preserves_valid_ast=False,
    preserves_typing=False,
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
    nature=MutationNature.SEMANTIC,
    severity=MutationSeverity.HIGH,
    severity_score=0.75,
    impact={MutationImpact.SEMANTIC_INVALID},
    expected_failures={
        PipelineStage.PARSING,
        PipelineStage.SEMANTIC_ANALYSIS,
    },
    preserves_valid_ast=False,
    preserves_typing=False,
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
    nature=MutationNature.STRUCTURAL,
    severity=MutationSeverity.MEDIUM,
    severity_score=0.5,
    impact={MutationImpact.PARSING},
    expected_failures={PipelineStage.PARSING},
    preserves_valid_ast=False,
    preserves_typing=False,
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


LEXICAL_MUTATIONS = [
    remove_random_character,
    inject_noise,
    corrupt_keyword,
    shuffle_lines,
]


def apply_lexical_mutations(program: str, n: int) -> str:

    mutated = program

    for _ in range(n):
        mutation_fn = random.choice(LEXICAL_MUTATIONS)
        mutated = mutation_fn(mutated)

    return mutated
