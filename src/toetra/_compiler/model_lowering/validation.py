from __future__ import annotations

from collections.abc import Iterable

from toetra._compiler.ir.ir1.nodes import ModelEvaluationIR
from toetra._compiler.ir.ir2.enums import AssumptionSource
from toetra._compiler.ir.ir2.errors import InvalidIR2InputError
from toetra._compiler.ir.ir2.guard import NNFGuard
from toetra._compiler.ir.ir2.model.base import ModelConstraintIR2
from toetra._compiler.ir.ir2.dsl.nodes import AssumptionIR2, NNFFormulaIR2
from toetra._compiler.model_lowering.errors import InvalidModelIRLoweringError


def validate_lowered_model_assumptions(
    assumptions: Iterable[AssumptionIR2],
    evaluations: tuple[ModelEvaluationIR, ...],
) -> tuple[AssumptionIR2, ...]:
    """Validate NNF shape, MODEL ownership, and evaluation coverage."""

    frozen = tuple(assumptions)
    requested = tuple(dict.fromkeys(evaluations))
    requested_set = set(requested)
    counts = {evaluation: 0 for evaluation in requested}

    for assumption in frozen:
        if assumption.source is not AssumptionSource.MODEL:
            raise InvalidModelIRLoweringError(
                "Model IR lowering may only emit source=MODEL assumptions."
            )
        if not isinstance(assumption.formula, NNFFormulaIR2):
            raise InvalidModelIRLoweringError(
                "Model IR lowering must emit NNFFormulaIR2 formulas."
            )
        try:
            NNFGuard.assert_expr_is_nnf(assumption.formula.expression)
        except InvalidIR2InputError as error:
            raise InvalidModelIRLoweringError(
                "Model IR lowering emitted a formula outside NNF."
            ) from error

        expression = assumption.formula.expression
        if not isinstance(expression, ModelConstraintIR2):
            continue
        evaluation = getattr(expression, "evaluation", None)
        if evaluation is None:
            continue
        if evaluation not in requested_set:
            raise InvalidModelIRLoweringError(
                "Model IR lowering emitted an unrequested model evaluation."
            )
        counts[evaluation] += 1

    missing = [evaluation for evaluation, count in counts.items() if count == 0]
    duplicate = [evaluation for evaluation, count in counts.items() if count > 1]
    if missing:
        labels = ", ".join(evaluation.point.name for evaluation in missing)
        raise InvalidModelIRLoweringError(
            "Model IR lowering omitted requested evaluation(s): " + labels
        )
    if duplicate:
        labels = ", ".join(evaluation.point.name for evaluation in duplicate)
        raise InvalidModelIRLoweringError(
            "Model IR lowering duplicated evaluation(s): " + labels
        )
    return frozen
