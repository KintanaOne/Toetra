from __future__ import annotations

from typing import List, Optional

from metadata.descriptor import MutationDescriptor
from metadata.enums import Layer, Domain, Strategy
from metadata.contract import PreservationLevel


class MutationFilterEngine:
    """
    Filtering system for mutation descriptors.

    Supports:
    - layer filtering
    - domain filtering
    - strategy filtering
    - contract-based constraints
    """

    def filter(
        self,
        items: List[MutationDescriptor],
        *,
        layer: Optional[Layer] = None,
        domain: Optional[Domain] = None,
        strategy: Optional[Strategy] = None,
        min_semantic_preservation: Optional[PreservationLevel] = None,
    ) -> List[MutationDescriptor]:

        result = items

        # -----------------------------------------------------
        # layer filter
        # -----------------------------------------------------
        if layer is not None:
            result = [
                d for d in result
                if d.layer == layer
            ]

        # -----------------------------------------------------
        # domain filter
        # -----------------------------------------------------
        if domain is not None:
            result = [
                d for d in result
                if d.domain == domain
            ]

        # -----------------------------------------------------
        # strategy filter
        # -----------------------------------------------------
        if strategy is not None:
            result = [
                d for d in result
                if d.strategy == strategy
            ]

        # -----------------------------------------------------
        # contract filter (semantic constraint)
        # -----------------------------------------------------
        if min_semantic_preservation is not None:

            def ok(d: MutationDescriptor) -> bool:
                return d.contract.semantics.value >= min_semantic_preservation.value

            result = [d for d in result if ok(d)]

        return result