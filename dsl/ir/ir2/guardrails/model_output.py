from __future__ import annotations

from typing import Any

from dsl.ir.ir1.nodes import AndIR, ComparisonIR, ImplyIR, NotIR, OrIR
from dsl.ir.ir2.enums import AssumptionSource
from dsl.ir.ir2.guardrails.diagnostics import DiagnosticSeverity, IR2Diagnostic

IR2_MODEL_OUTPUT_NOT_REFERENCED = "IR2_MODEL_OUTPUT_NOT_REFERENCED"


def diagnose_model_output_not_referenced(task: Any) -> tuple[IR2Diagnostic, ...]:
    """
    Emit a warning when model assumptions are present but the user spec
    does not reference any model output symbol.

    This is not invalid:
        x0.age <= 30

    But when model assumptions are injected, it means the property may be
    an input/domain constraint rather than a model-behavior constraint.
    """

    assumptions = tuple(getattr(task, "assumptions", ()))

    has_model_assumption = any(
        assumption.source is AssumptionSource.MODEL for assumption in assumptions
    )

    if not has_model_assumption:
        return ()

    spec_formula = getattr(task, "spec_formula", None)

    if spec_formula is None:
        return ()

    if _formula_references_model_output(spec_formula):
        return ()

    return (
        IR2Diagnostic(
            code=IR2_MODEL_OUTPUT_NOT_REFERENCED,
            severity=DiagnosticSeverity.WARNING,
            message=(
                "Model assumptions were injected, but the specification does not "
                "reference any model output symbol such as '_model.<target>'. "
                "This property may still be valid as an input/domain constraint, "
                "but it does not constrain model behavior directly."
            ),
        ),
    )


def _formula_references_model_output(formula: Any) -> bool:
    expression = getattr(formula, "expression", formula)

    return _expression_references_model_output(expression)


def _expression_references_model_output(expression: Any) -> bool:
    if isinstance(expression, ComparisonIR):
        return expression.entity == "_model"

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

    # Future-proofing for model-side IR2 nodes such as AffineOutputConstraintIR2.
    output_entity = getattr(expression, "output_entity", None)

    if output_entity == "_model":
        return True

    entity = getattr(expression, "entity", None)

    return entity == "_model"
