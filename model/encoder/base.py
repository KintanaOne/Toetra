from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from dsl.ir.ir1.nodes import ModelEvaluationIR
from dsl.ir.ir2.enums import AssumptionSource
from dsl.ir.ir2.errors import InvalidIR2InputError
from dsl.ir.ir2.guard import NNFGuard
from dsl.ir.ir2.model.base import ModelConstraintIR2
from dsl.ir.ir2.nodes import AssumptionIR2, NNFFormulaIR2
from model.encoder.context import ModelEncodingContext
from model.encoder.errors import InvalidModelAssumptionError
from model.schema.model_schema import ModelSchema


class ModelEncoder(Protocol):
    """Backend-independent model-to-IR2 assumption encoder.

    Implementations translate a normalized ``ModelSchema`` and an explicit set
    of requested model evaluations into MODEL assumptions expressed as IR2 NNF
    formulas. They must not inspect a legacy scope and guess which point feeds
    the model.
    """

    def encode(
        self,
        schema: ModelSchema,
        evaluations: tuple[ModelEvaluationIR, ...],
        *,
        context: ModelEncodingContext | None = None,
    ) -> tuple[AssumptionIR2, ...]:
        """Return one model constraint for each requested evaluation."""
        ...


def validate_model_assumptions(
    assumptions: Iterable[AssumptionIR2],
) -> tuple[AssumptionIR2, ...]:
    """Validate and freeze assumptions emitted by a ModelEncoder.

    The encoder boundary is intentionally strict:
    - every emitted assumption must be tagged as MODEL,
    - every emitted formula must be NNFFormulaIR2,
    - the wrapped IR1 expression must satisfy the NNF contract,
    - structured model constraints must not duplicate one evaluation identity.
    """

    frozen = tuple(assumptions)
    seen_evaluations: set[object] = set()

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

        expression = assumption.formula.expression
        if isinstance(expression, ModelConstraintIR2):
            evaluation = getattr(expression, "evaluation", None)
            if evaluation is not None:
                if evaluation in seen_evaluations:
                    raise InvalidModelAssumptionError(
                        "ModelEncoder emitted more than one constraint for the same "
                        "model evaluation."
                    )
                seen_evaluations.add(evaluation)

    return frozen


def validate_model_evaluation_coverage(
    assumptions: tuple[AssumptionIR2, ...],
    evaluations: tuple[ModelEvaluationIR, ...],
) -> None:
    """Ensure requested evaluations are connected exactly once.

    Generic non-model atoms may coexist in MODEL assumptions, but every
    structured model constraint carrying an evaluation must correspond to one
    requested identity, and each requested identity must be covered once.
    """

    requested = tuple(dict.fromkeys(evaluations))
    requested_set = set(requested)
    counts = {evaluation: 0 for evaluation in requested}

    for assumption in assumptions:
        expression = assumption.formula.expression
        if not isinstance(expression, ModelConstraintIR2):
            continue
        evaluation = getattr(expression, "evaluation", None)
        if evaluation is None:
            continue
        if evaluation not in requested_set:
            raise InvalidModelAssumptionError(
                "ModelEncoder emitted a constraint for an unrequested model "
                f"evaluation at point {evaluation.point.name!r}."
            )
        counts[evaluation] += 1

    missing = [evaluation for evaluation, count in counts.items() if count == 0]
    duplicate = [evaluation for evaluation, count in counts.items() if count > 1]

    if missing:
        labels = ", ".join(evaluation.point.name for evaluation in missing)
        raise InvalidModelAssumptionError(
            "ModelEncoder did not emit a constraint for requested evaluation(s): "
            f"{labels}."
        )
    if duplicate:
        labels = ", ".join(evaluation.point.name for evaluation in duplicate)
        raise InvalidModelAssumptionError(
            "ModelEncoder emitted duplicate constraints for evaluation(s): "
            f"{labels}."
        )
