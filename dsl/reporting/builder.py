from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from dsl.backends.results import VerificationResult
from dsl.backends.router import BackendRoute
from dsl.ir.ir1.nodes import (
    AndIR,
    AtomicIR,
    ComparisonIR,
    LogicalIR,
    NotIR,
    OrIR,
    ProblemIR,
)
from dsl.ir.ir1.scalar import format_scalar_expression
from dsl.ir.ir2.nodes import NNFFormulaIR2, VerificationTaskIR2
from dsl.reporting.model import (
    ReportAssignment,
    ReportAssignmentKind,
    ReportScope,
    ReportScopeVariable,
    VerificationReport,
)


def build_verification_report(
    task: VerificationTaskIR2,
    route: BackendRoute,
    result: VerificationResult,
    *,
    property_index: int,
) -> VerificationReport:
    """Combine an IR2 task, routing decision and backend result into a report."""

    if result.backend is not route.backend:
        raise ValueError(
            "Backend result does not match the selected route: "
            f"result={result.backend.value}, route={route.backend.value}"
        )

    return VerificationReport(
        property_index=property_index,
        property_type=task.property_type,
        semantics=task.semantics,
        scope=_build_scope(task),
        specification=_format_specification(task.spec_formula),
        backend=result.backend,
        backend_status=result.backend_status,
        status=result.status,
        summary=result.message,
        assignments=_build_assignments(result.assignments),
        diagnostics=result.diagnostics,
        assumption_count=len(task.assumptions),
        route_reason=route.reason,
    )


def _build_scope(task: VerificationTaskIR2) -> ReportScope:
    return ReportScope(
        kind=task.scope.kind,
        quantifier=task.scope.quantifier,
        variables=tuple(
            ReportScopeVariable(name=name, role=role)
            for name, role in task.scope.variables.items()
        ),
    )


def _build_assignments(
    assignments: Mapping[str, Any] | None,
) -> tuple[ReportAssignment, ...]:
    if not assignments:
        return ()

    return tuple(
        _build_assignment(name, value) for name, value in sorted(assignments.items())
    )


def _build_assignment(name: str, value: Any) -> ReportAssignment:
    if name.startswith("_model."):
        return ReportAssignment(
            raw_name=name,
            display_name=name.removeprefix("_model."),
            value=value,
            kind=ReportAssignmentKind.OUTPUT,
        )

    if "." in name:
        return ReportAssignment(
            raw_name=name,
            display_name=name,
            value=value,
            kind=ReportAssignmentKind.INPUT,
        )

    return ReportAssignment(
        raw_name=name,
        display_name=name,
        value=value,
        kind=ReportAssignmentKind.AUXILIARY,
    )


def _format_specification(formula: NNFFormulaIR2) -> str:
    return _format_logical(formula.expression)


def _format_logical(node: LogicalIR) -> str:
    if isinstance(node, ComparisonIR):
        left = format_scalar_expression(node.left)
        right = format_scalar_expression(node.right)
        return f"{left} {node.op.value} {right}"

    if isinstance(node, ProblemIR):
        function = getattr(node.function, "value", node.function)
        return f"{node.problem.value}.{function}({node.args or {}})"

    if isinstance(node, NotIR):
        return f"not ({_format_logical(node.operand)})"

    if isinstance(node, AndIR):
        return _join_logical("and", node.operands)

    if isinstance(node, OrIR):
        return _join_logical("or", node.operands)

    if isinstance(node, AtomicIR):
        return repr(node)

    raise TypeError(f"Unsupported report specification node: {type(node).__name__}")


def _join_logical(operator: str, operands: list[LogicalIR]) -> str:
    return f" {operator} ".join(f"({_format_logical(item)})" for item in operands)
