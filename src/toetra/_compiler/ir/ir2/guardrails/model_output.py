from __future__ import annotations

from collections import Counter
from typing import Any

from toetra._compiler.ir.ir1.nodes import AndIR, ComparisonIR, ImplyIR, NotIR, OrIR
from toetra._compiler.ir.ir1.scalar import references_model_output
from toetra._compiler.ir.ir2.enums import AssumptionSource
from toetra._compiler.ir.ir2.guardrails.diagnostics import (
    DiagnosticSeverity,
    IR2Diagnostic,
)
from toetra._compiler.ir.ir2.model.base import ModelConstraintIR2

IR2_MODEL_OUTPUT_NOT_REFERENCED = "IR2_MODEL_OUTPUT_NOT_REFERENCED"
MODEL_EVALUATION_MISSING = "MODEL_EVALUATION_MISSING"
MODEL_EVALUATION_DUPLICATE = "MODEL_EVALUATION_DUPLICATE"
MODEL_EVALUATION_DISCONNECTED = "MODEL_EVALUATION_DISCONNECTED"


def diagnose_model_output_not_referenced(task: Any) -> tuple[IR2Diagnostic, ...]:
    """Warn about legacy/manual model assumptions disconnected from the spec."""

    assumptions = tuple(getattr(task, "assumptions", ()))
    has_model_assumption = any(
        assumption.source is AssumptionSource.MODEL for assumption in assumptions
    )
    if not has_model_assumption:
        return ()

    spec_formula = getattr(task, "spec_formula", None)
    if spec_formula is None or _formula_references_model_output(spec_formula):
        return ()

    return (
        IR2Diagnostic(
            code=IR2_MODEL_OUTPUT_NOT_REFERENCED,
            severity=DiagnosticSeverity.WARNING,
            message=(
                "Model assumptions were injected, but the specification does not "
                "reference any model output. Evaluation-driven ModelBridge callers "
                "should normally emit no model equation for this task."
            ),
        ),
    )


def diagnose_model_evaluation_connectivity(task: Any) -> tuple[IR2Diagnostic, ...]:
    """Compare required evaluations with structured model equations."""

    required = tuple(getattr(task, "model_evaluations", ()))
    required_set = set(required)
    counts: Counter[Any] = Counter()

    for assumption in tuple(getattr(task, "assumptions", ())):
        if assumption.source is not AssumptionSource.MODEL:
            continue
        expression = assumption.formula.expression
        if not isinstance(expression, ModelConstraintIR2):
            continue
        evaluation = getattr(expression, "evaluation", None)
        if evaluation is not None:
            counts[evaluation] += 1

    diagnostics: list[IR2Diagnostic] = []

    for evaluation in required:
        count = counts[evaluation]
        if count == 0:
            diagnostics.append(
                IR2Diagnostic(
                    code=MODEL_EVALUATION_MISSING,
                    severity=DiagnosticSeverity.WARNING,
                    message=(
                        "No model equation is connected to required evaluation "
                        f"target[{evaluation.point.name}] for model "
                        f"{evaluation.model_identity!r}."
                    ),
                )
            )
        elif count > 1:
            diagnostics.append(
                IR2Diagnostic(
                    code=MODEL_EVALUATION_DUPLICATE,
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        f"{count} model equations are connected to evaluation "
                        f"target[{evaluation.point.name}]; exactly one is required."
                    ),
                )
            )

    for evaluation, count in counts.items():
        if evaluation in required_set:
            continue
        diagnostics.append(
            IR2Diagnostic(
                code=MODEL_EVALUATION_DISCONNECTED,
                severity=DiagnosticSeverity.WARNING,
                message=(
                    f"Model equation for target[{evaluation.point.name}] is not "
                    "requested by the specification."
                ),
            )
        )
        if count > 1:
            diagnostics.append(
                IR2Diagnostic(
                    code=MODEL_EVALUATION_DUPLICATE,
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        f"{count} disconnected model equations share evaluation "
                        f"target[{evaluation.point.name}]."
                    ),
                )
            )

    return tuple(diagnostics)


def _formula_references_model_output(formula: Any) -> bool:
    expression = getattr(formula, "expression", formula)
    return _expression_references_model_output(expression)


def _expression_references_model_output(expression: Any) -> bool:
    if isinstance(expression, ComparisonIR):
        return references_model_output(expression.left) or references_model_output(
            expression.right
        )

    if isinstance(expression, AndIR):
        return any(
            _expression_references_model_output(op) for op in expression.operands
        )

    if isinstance(expression, OrIR):
        return any(
            _expression_references_model_output(op) for op in expression.operands
        )

    if isinstance(expression, NotIR):
        return _expression_references_model_output(expression.operand)

    if isinstance(expression, ImplyIR):
        return _expression_references_model_output(
            expression.left
        ) or _expression_references_model_output(expression.right)

    output_entity = getattr(expression, "output_entity", None)
    if output_entity == "_model":
        return True

    entity = getattr(expression, "entity", None)
    return entity == "_model"
