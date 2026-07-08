from __future__ import annotations

import random
from typing import List, Optional

from metadata.descriptor import MutationDescriptor
from metadata.enums import Layer, Domain, Strategy


class MutationSelectionEngine:
    """
    Intelligent mutation sampler for Hypothesis or fuzzing.

    Supports weighted or constrained selection.
    """

    def __init__(self, seed: Optional[int] = None):
        self.random = random.Random(seed)

    # ---------------------------------------------------------
    # main entrypoint
    # ---------------------------------------------------------

    def select(
        self,
        items: List[MutationDescriptor],
        *,
        layer: Optional[Layer] = None,
        domain: Optional[Domain] = None,
        strategy: Optional[Strategy] = None,
    ) -> MutationDescriptor:
        """
        Select a single mutation matching constraints.
        """

        filtered = items

        # -----------------------------------------------------
        # constraints
        # -----------------------------------------------------
        if layer is not None:
            filtered = [d for d in filtered if d.layer == layer]

        if domain is not None:
            filtered = [d for d in filtered if d.domain == domain]

        if strategy is not None:
            filtered = [d for d in filtered if d.strategy == strategy]

        if not filtered:
            raise ValueError("No mutation matches constraints")

        # -----------------------------------------------------
        # sampling strategy (simple v1)
        # -----------------------------------------------------
        return self.random.choice(filtered)
