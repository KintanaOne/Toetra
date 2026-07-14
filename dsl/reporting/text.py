from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from textwrap import wrap

from dsl.backends.diagnostics import BackendResultDiagnostic
from dsl.backends.results import VerificationStatus
from dsl.reporting.model import (
    ReportAssignment,
    ReportAssignmentKind,
    VerificationReport,
)


@dataclass(frozen=True)
class TextRenderOptions:
    """Configuration shared by the terminal-oriented report renderers."""

    width: int = 80
    use_unicode: bool = True
    include_route_reason: bool = True

    def __post_init__(self) -> None:
        if self.width < 48:
            raise ValueError("Text report width must be at least 48 characters")


def render_verification_report_text(
    report: VerificationReport,
    *,
    options: TextRenderOptions | None = None,
) -> str:
    """Render one backend-neutral verification report as readable plain text."""

    resolved = options or TextRenderOptions()
    separator = "━" if resolved.use_unicode else "="
    lines = [
        separator * resolved.width,
        f"FORML Verification Report · Property {report.property_index + 1}",
        separator * resolved.width,
        "",
        _field("Status", _status_label(report.status, resolved.use_unicode)),
        _field("Property", report.property_type.value),
        _field("Semantics", report.semantics.value),
        _field("Scope", _format_scope(report)),
        _field("Specification", report.specification),
        _field("Backend", f"{report.backend.value} ({report.backend_status})"),
        _field("Assumptions", str(report.assumption_count)),
    ]

    if resolved.include_route_reason:
        lines.append(_field("Route", report.route_reason))

    lines.extend(["", "Conclusion"])
    lines.extend(
        _indented_wrapped(report.summary or "No summary was provided.", resolved)
    )

    if report.assignments:
        lines.extend(["", _assignment_section_title(report.status)])
        lines.extend(_render_assignment_groups(report, resolved))

    if report.diagnostics:
        lines.extend(["", "Diagnostics"])
        for diagnostic in report.diagnostics:
            lines.extend(_render_diagnostic(diagnostic, resolved))

    return "\n".join(lines).rstrip()


def render_verification_reports_text(
    reports: Iterable[VerificationReport],
    *,
    options: TextRenderOptions | None = None,
) -> str:
    """Render several reports using the same stable text representation."""

    resolved = options or TextRenderOptions()
    rendered = [
        render_verification_report_text(report, options=resolved) for report in reports
    ]
    return "\n\n".join(rendered)


def _field(label: str, value: str) -> str:
    return f"{label:<14}: {value}"


def _status_label(status: VerificationStatus, use_unicode: bool) -> str:
    unicode_symbols = {
        VerificationStatus.PROVED: "✓",
        VerificationStatus.COUNTEREXAMPLE: "✗",
        VerificationStatus.WITNESS: "✓",
        VerificationStatus.NO_WITNESS: "○",
        VerificationStatus.UNKNOWN: "?",
    }
    ascii_symbols = {
        VerificationStatus.PROVED: "PASS",
        VerificationStatus.COUNTEREXAMPLE: "FAIL",
        VerificationStatus.WITNESS: "FOUND",
        VerificationStatus.NO_WITNESS: "NONE",
        VerificationStatus.UNKNOWN: "UNKNOWN",
    }
    symbol = (unicode_symbols if use_unicode else ascii_symbols)[status]
    return f"{symbol} {status.value.upper()}"


def _format_scope(report: VerificationReport) -> str:
    variable_names = ", ".join(variable.name for variable in report.scope.variables)
    if report.scope.quantifier:
        return " ".join(
            part for part in (report.scope.quantifier, variable_names) if part
        )
    if variable_names:
        return f"{report.scope.kind} {variable_names}"
    return report.scope.kind


def _assignment_section_title(status: VerificationStatus) -> str:
    if status is VerificationStatus.COUNTEREXAMPLE:
        return "Counterexample"
    if status is VerificationStatus.WITNESS:
        return "Witness"
    return "Backend assignments"


def _render_assignment_groups(
    report: VerificationReport,
    options: TextRenderOptions,
) -> list[str]:
    lines: list[str] = []
    groups = (
        ("Inputs", ReportAssignmentKind.INPUT, report.inputs),
        ("Model outputs", ReportAssignmentKind.OUTPUT, report.outputs),
        (
            "Auxiliary values",
            ReportAssignmentKind.AUXILIARY,
            report.auxiliary_assignments,
        ),
    )
    for label, _kind, assignments in groups:
        if not assignments:
            continue
        lines.append(f"  {label}")
        for assignment in assignments:
            lines.extend(_render_assignment(assignment, options))
    return lines


def _render_assignment(
    assignment: ReportAssignment,
    options: TextRenderOptions,
) -> list[str]:
    text = f"{assignment.display_name} = {assignment.value}"
    return [f"    {line}" for line in wrap(text, width=max(20, options.width - 4))]


def _render_diagnostic(
    diagnostic: BackendResultDiagnostic,
    options: TextRenderOptions,
) -> list[str]:
    prefix = f"[{diagnostic.severity.value.upper()}] {diagnostic.code}: "
    wrapped = wrap(
        prefix + diagnostic.message,
        width=max(20, options.width - 2),
        subsequent_indent="  ",
    )
    return [f"  {line}" for line in wrapped]


def _indented_wrapped(text: str, options: TextRenderOptions) -> list[str]:
    return [
        f"  {line}" for line in wrap(text, width=max(20, options.width - 2)) or [""]
    ]
