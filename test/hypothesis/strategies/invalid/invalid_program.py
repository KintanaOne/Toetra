"""
Multi-layer invalid FORML generation.

This module orchestrates corruption across
the FORML compilation pipeline.

It does NOT contain mutation logic.

Mutation selection is delegated to the
generic mutation engine.
"""

from __future__ import annotations

import random
from hypothesis import strategies as st

from hypothesis.strategies import composite

from dsl.parser.parser import parse_toetra_code
from dsl.builder.program import parse_program

from test.hypothesis.strategies.valid.valid_lexical import (
    valid_lexical_program,
)

from test.hypothesis.strategies.invalid.generic import (
    invalid_program_for,
)

from test.hypothesis.mutation.metadata.enums import (
    Layer,
    Strategy,
)


@composite
def invalid_program(
    draw,
    registry,
    filter_engine,
    *,
    string_ratio: float = 0.4,
    cst_ratio: float = 0.3,
    ast_ratio: float = 0.3,
):
    """
    Generate invalid artifacts at different
    compilation stages.

    Corruption may happen at:

        - raw text
        - CST
        - AST
    """

    program = draw(valid_lexical_program())

    # ------------------------------------------
    # STRING
    # ------------------------------------------

    if random.random() < string_ratio:

        program = draw(
            invalid_program_for(
                base_strategy=st.just(program),
                registry=registry,
                filter_engine=filter_engine,
                artifact_layer=Layer.STRING,
                layer=Layer.STRING,
                strategy=Strategy.CORRUPTED,
            )
        )

    try:
        cst = parse_toetra_code(program)

    except Exception:

        return program

    # ------------------------------------------
    # CST
    # ------------------------------------------

    if random.random() < cst_ratio:

        cst = draw(
            invalid_program_for(
                base_strategy=st.just(cst),
                registry=registry,
                filter_engine=filter_engine,
                artifact_layer=Layer.CST,
                layer=Layer.CST,
                strategy=Strategy.CORRUPTED,
            )
        )

    try:
        ast = parse_program(cst)

    except Exception:

        return cst

    # ------------------------------------------
    # AST
    # ------------------------------------------

    if random.random() < ast_ratio:

        ast = draw(
            invalid_program_for(
                base_strategy=st.just(ast),
                registry=registry,
                filter_engine=filter_engine,
                artifact_layer=Layer.AST,
                layer=Layer.AST,
            )
        )

    return ast
