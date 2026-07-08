from __future__ import annotations

from collections.abc import Iterable

from dsl.ir.ir2.errors import InvalidIR2InputError
from dsl.ir.ir2.guard import NNFGuard
from dsl.ir.ir2.nodes import AssumptionIR2, NNFFormulaIR2


class AssumptionCollector:
    """Collect and validate assumptions produced by upstream components.

    IR2 deliberately does not encode ML models itself. Future ModelEncoder
    components can pass MODEL assumptions into IR2Builder. This collector is
    the boundary guard between external assumption producers and IR2.

    Contract:
        - assumptions are immutable once collected;
        - every item must be an AssumptionIR2;
        - every assumption formula must be NNFFormulaIR2;
        - every assumption expression must already satisfy NNF.

    Normal-form adaptation is intentionally not done here. IR2 first aggregates
    all assumptions into Γ, builds Γ ∧ ¬P, and only then selects CNF/DNF/NNF.
    """

    def collect(
        self,
        assumptions: tuple[AssumptionIR2, ...] | list[AssumptionIR2] | None = None,
    ) -> tuple[AssumptionIR2, ...]:
        if assumptions is None:
            return ()

        collected = tuple(self._iter_assumptions(assumptions))

        for index, assumption in enumerate(collected):
            self._validate_assumption(assumption, index=index)

        return collected

    def _iter_assumptions(
        self,
        assumptions: Iterable[AssumptionIR2],
    ) -> Iterable[AssumptionIR2]:
        for assumption in assumptions:
            yield assumption

    def _validate_assumption(self, assumption: AssumptionIR2, *, index: int) -> None:
        if not isinstance(assumption, AssumptionIR2):
            raise InvalidIR2InputError(
                f"IR2 assumption at index {index} must be AssumptionIR2, "
                f"got {type(assumption).__name__}."
            )

        if not isinstance(assumption.formula, NNFFormulaIR2):
            raise InvalidIR2InputError(
                f"IR2 assumption at index {index} must contain NNFFormulaIR2, "
                f"got {type(assumption.formula).__name__}."
            )

        try:
            NNFGuard.assert_expr_is_nnf(assumption.formula.expression)
        except InvalidIR2InputError as e:
            raise InvalidIR2InputError(
                f"IR2 assumption at index {index} is not valid NNF: {e}"
            ) from e
