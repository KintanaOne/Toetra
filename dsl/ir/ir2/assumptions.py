from __future__ import annotations

from dsl.ir.ir2.nodes import AssumptionIR2


class AssumptionCollector:
    """Collects assumptions already produced by upstream components.

    IR2 deliberately does not encode ML models itself. Future ModelEncoder
    components can pass MODEL assumptions into IR2Builder. This collector simply
    normalizes the optional input into an immutable tuple.
    """

    def collect(
        self,
        assumptions: tuple[AssumptionIR2, ...] | list[AssumptionIR2] | None = None,
    ) -> tuple[AssumptionIR2, ...]:
        if assumptions is None:
            return ()
        return tuple(assumptions)
