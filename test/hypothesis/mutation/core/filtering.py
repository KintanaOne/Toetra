from __future__ import annotations

from typing import List, Optional

from metadata.descriptor import MutationDescriptor
from metadata.enums import Layer, Domain, Nature, Strategy
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
        nature: Optional[Nature] = None,
        min_severity: Optional[float] = None,
        max_severity: Optional[float] = None,
    ) -> List[MutationDescriptor]:

        result = items

        # -----------------------------------------------------
        # layer filter
        # -----------------------------------------------------
        if layer is not None:
            result = [d for d in result if d.layer == layer]

        # -----------------------------------------------------
        # domain filter
        # -----------------------------------------------------
        if domain is not None:
            result = [d for d in result if d.domain == domain]

        # -----------------------------------------------------
        # strategy filter
        # -----------------------------------------------------
        if strategy is not None:
            result = [d for d in result if d.strategy == strategy]

        # -----------------------------------------------------
        # contract filter (semantic constraint)
        # -----------------------------------------------------
        if min_semantic_preservation is not None:

            def ok(d: MutationDescriptor) -> bool:
                return d.contract.semantics.value >= min_semantic_preservation.value

            result = [d for d in result if ok(d)]

        # -----------------------------------------------------
        # nature filter
        # -----------------------------------------------------
        if nature is not None:
            result = [d for d in result if d.nature == nature]

        # -----------------------------------------------------
        # severity filter
        # -----------------------------------------------------
        if min_severity is not None or max_severity is not None:

            def ok(d: MutationDescriptor) -> bool:
                assert (
                    d.severity is not None
                ), "Descriptor severity must be set for severity-based filtering"
                if min_severity is not None and d.severity < min_severity:
                    return False
                if max_severity is not None and d.severity > max_severity:
                    return False
                return True

            result = [d for d in result if ok(d)]

        return result
