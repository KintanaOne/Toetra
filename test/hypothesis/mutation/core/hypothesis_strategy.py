from __future__ import annotations

from hypothesis import strategies as st

from registry import MutationRegistry
from filtering import MutationFilterEngine


def mutation_strategy(
    registry: MutationRegistry,
    filter_engine: MutationFilterEngine,
    **filters,
):
    """
    Generate Hypothesis strategies from mutation descriptors.
    """

    descriptors = registry.filter(
        engine=filter_engine,
        **filters,
    )

    return st.sampled_from(descriptors)