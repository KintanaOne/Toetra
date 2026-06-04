"""
Generic mutation-based strategy generation.

This module provides a metadata-driven mutation engine.

Instead of hardcoding mutation families
(lexical, syntactic, semantic, etc.),

mutations are selected dynamically from
the MutationRegistry using descriptor metadata.

This is the preferred entrypoint for mutation
campaigns in FORML.
"""

from __future__ import annotations

from hypothesis import strategies as st

from test.hypothesis.mutation.core.artifact import Artifact
from test.hypothesis.mutation.core.pipeline import MutationPipeline
from test.hypothesis.mutation.core.registry import MutationRegistry
from test.hypothesis.mutation.core.filtering import MutationFilterEngine
from test.hypothesis.mutation.core.hypothesis_strategy import (
    mutation_strategy,
)
from test.hypothesis.mutation.metadata.enums import Layer


@st.composite
def invalid_program_for(
    draw,
    base_strategy,
    registry: MutationRegistry,
    filter_engine: MutationFilterEngine,
    *,
    artifact_layer: Layer,
    mutation_count_min: int = 1,
    mutation_count_max: int = 3,
    heavy_corruption_probability: float = 0.5,
    **filters,
):
    """
    Generate a mutated artifact using registry metadata.

    Selection is entirely descriptor-driven.

    Examples
    --------

    Lexical corruption:

        invalid_program_for(
            layer=Layer.STRING,
            strategy=Strategy.CORRUPTED,
        )

    Semantic corruption:

        invalid_program_for(
            layer=Layer.AST,
            domain=Domain.SEMANTIC,
        )
    """

    value = draw(base_strategy)

    mutation_count = draw(
        st.integers(
            min_value=mutation_count_min,
            max_value=mutation_count_max,
        )
    )

    if draw(st.booleans()):
        mutation_count *= 2

    mutations = []

    for _ in range(mutation_count):

        descriptor = draw(
            mutation_strategy(
                registry,
                filter_engine,
                **filters,
            )
        )

        mutations.append(
            descriptor.mutation
        )

    pipeline = MutationPipeline(
        mutations
    )

    artifact = Artifact(
        value=value,
        layer=artifact_layer,
    )

    return pipeline.run(
        artifact
    ).value