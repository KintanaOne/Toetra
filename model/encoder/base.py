from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from dsl.ir.ir1.nodes import ScopeIR
from dsl.ir.ir2.enums import AssumptionSource
from dsl.ir.ir2.errors import InvalidIR2InputError
from dsl.ir.ir2.guard import NNFGuard
from dsl.ir.ir2.nodes import AssumptionIR2, NNFFormulaIR2
from model.encoder.context import ModelEncodingContext
from model.encoder.errors import InvalidModelAssumptionError
from model.schema.model_schema import ModelSchema


class ModelEncoder(Protocol):
    """Backend-independent model-to-IR2 assumption encoder.

    Implementations translate a normalized ModelSchema into MODEL assumptions
    expressed as IR2 NNF formulas. They must not create Z3 expressions, select
    a backend, or decide the final CNF/DNF/NNF form of the full verification
    condition.
    """

    def encode(
        self,
        schema: ModelSchema,
        scope: ScopeIR,
        *,
        context: ModelEncodingContext | None = None,
    ) -> tuple[AssumptionIR2, ...]:
        """Return MODEL assumptions in NNF form."""
        ...


def validate_model_assumptions(
    assumptions: Iterable[AssumptionIR2],
) -> tuple[AssumptionIR2, ...]:
    """Validate and freeze assumptions emitted by a ModelEncoder.

    The encoder boundary is intentionally strict:
    - every emitted assumption must be tagged as MODEL,
    - every emitted formula must be NNFFormulaIR2,
    - the wrapped IR1 expression must satisfy the NNF contract.
    """

    frozen = tuple(assumptions)

    for assumption in frozen:
        if assumption.source != AssumptionSource.MODEL:
            raise InvalidModelAssumptionError(
                "ModelEncoder may only emit assumptions with source=MODEL."
            )

        if not isinstance(assumption.formula, NNFFormulaIR2):
            raise InvalidModelAssumptionError(
                "ModelEncoder assumptions must wrap NNFFormulaIR2 formulas."
            )

        try:
            NNFGuard.assert_expr_is_nnf(assumption.formula.expression)
        except InvalidIR2InputError as exc:
            raise InvalidModelAssumptionError(
                "ModelEncoder emitted a formula that does not satisfy NNF."
            ) from exc

    return frozen
