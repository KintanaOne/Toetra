from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from textwrap import wrap

from toetra._backends.diagnostics import BackendResultDiagnostic
from toetra._backends.results import VerificationStatus
from toetra._reporting.model import (
    ReportAssignment,
    ReportAssignmentKind,
    VerificationReport,
)
from toetra._reporting.evaluations import ReportLoweringTrace


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
        f"Toetra Verification Report · Property {report.property_index + 1}",
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

    provenance = report.provenance
    if provenance is not None:
        lines.extend(
            [
                _field(
                    "Verification",
                    provenance.verification_fingerprint.split(":", 1)[-1][:12],
                ),
                _field("Captured", provenance.captured_at_utc),
                _field("Provenance", provenance.completeness.value),
            ]
        )

    if resolved.include_route_reason:
        lines.append(_field("Route", report.route_reason))

    execution = report.backend_execution
    if execution is not None:
        lines.extend(
            [
                _field("Execution", execution.status),
                _field("Duration", f"{execution.duration_ms:.3f} ms"),
                _field(
                    "Timeout",
                    (
                        "disabled"
                        if execution.timeout_ms is None
                        else f"{execution.timeout_ms} ms"
                    ),
                ),
                _field(
                    "Backend units",
                    (
                        "unbounded"
                        if execution.max_backend_units is None
                        else str(execution.max_backend_units)
                    ),
                ),
                _field(
                    "Memory",
                    (
                        "unbounded"
                        if execution.max_memory_mb is None
                        else f"{execution.max_memory_mb} MB"
                    ),
                ),
                _field(
                    "Seed",
                    (
                        "default"
                        if execution.deterministic_seed is None
                        else str(execution.deterministic_seed)
                    ),
                ),
                _field(
                    "Backend opts",
                    _format_backend_options(execution.backend_options),
                ),
            ]
        )
        if execution.reason is not None:
            lines.append(_field("Exec reason", execution.reason))
        if execution.backend_reason is not None:
            lines.append(_field("Native reason", execution.backend_reason))

    compatibility = report.numeric_compatibility
    if compatibility is not None:
        lines.extend(
            [
                _field(
                    "Numeric route",
                    f"{compatibility.classification} ({compatibility.support_status})",
                ),
                _field("Semantic target", compatibility.semantic_target),
                _field("Claim scope", compatibility.conclusion_scope),
                _field(
                    "Numeric rule",
                    compatibility.matched_rule_id or "<no matching rule>",
                ),
            ]
        )

    lines.extend(["", "Conclusion"])
    lines.extend(
        _indented_wrapped(report.summary or "No summary was provided.", resolved)
    )

    if report.assignments:
        lines.extend(["", _assignment_section_title(report.status)])
        if report.points:
            lines.extend(_render_point_groups(report, resolved))
        else:
            lines.extend(_render_assignment_groups(report, resolved))

    if report.model_evaluations:
        lines.extend(["", "Model evaluations"])
        lines.extend(_render_model_evaluations(report, resolved))

    if compatibility is not None:
        lines.extend(["", "Numeric compatibility"])
        lines.extend(
            _indented_wrapped(
                f"Source: {compatibility.source_route}",
                resolved,
            )
        )
        lines.extend(
            _indented_wrapped(
                f"Backend: {compatibility.backend_route}",
                resolved,
            )
        )
        lines.extend(
            _indented_wrapped(
                "Encoder: "
                f"{compatibility.model_encoder_id}@"
                f"{compatibility.model_encoder_version}",
                resolved,
            )
        )
        if compatibility.evidence_id is not None:
            lines.extend(
                _indented_wrapped(
                    f"Evidence: {compatibility.evidence_id}",
                    resolved,
                )
            )
        if compatibility.property_numeric_requirements:
            lines.extend(
                _indented_wrapped(
                    "Requirements: "
                    + ", ".join(compatibility.property_numeric_requirements),
                    resolved,
                )
            )
        if compatibility.permitted_conclusions:
            lines.extend(
                _indented_wrapped(
                    "Permitted conclusions: "
                    + ", ".join(compatibility.permitted_conclusions),
                    resolved,
                )
            )
        if compatibility.replay_required_for:
            lines.extend(
                _indented_wrapped(
                    "Replay required for: "
                    + ", ".join(compatibility.replay_required_for),
                    resolved,
                )
            )
        if compatibility.assumptions_and_preconditions:
            lines.append("  Preconditions")
            for item in compatibility.assumptions_and_preconditions:
                lines.extend(
                    f"    {line}"
                    for line in wrap(
                        "- " + item,
                        width=max(20, resolved.width - 4),
                        subsequent_indent="  ",
                    )
                )
        if compatibility.compatibility_diagnostics:
            lines.append("  Compatibility diagnostics")
            for item in compatibility.compatibility_diagnostics:
                lines.extend(
                    f"    {line}"
                    for line in wrap(
                        "- " + item,
                        width=max(20, resolved.width - 4),
                        subsequent_indent="  ",
                    )
                )
        if compatibility.documentation_reference is not None:
            lines.extend(
                _indented_wrapped(
                    f"Documentation: {compatibility.documentation_reference}",
                    resolved,
                )
            )

    if provenance is not None:
        lines.extend(["", "Verification provenance"])
        lines.extend(
            _indented_wrapped(
                f"Inputs: {provenance.input_fingerprint}",
                resolved,
            )
        )
        lines.extend(
            _indented_wrapped(
                f"Property: {provenance.property_fingerprint}",
                resolved,
            )
        )
        lines.extend(
            _indented_wrapped(
                f"Route: {provenance.route_fingerprint}",
                resolved,
            )
        )
        lines.extend(
            _indented_wrapped(
                f"Execution policy: {provenance.execution_policy_fingerprint}",
                resolved,
            )
        )
        lines.extend(
            _indented_wrapped(
                f"Verification: {provenance.verification_fingerprint}",
                resolved,
            )
        )
        lines.extend(
            _indented_wrapped(
                f"Toetra: {provenance.software.toetra_version}"
                + (
                    f" ({provenance.software.toetra_build_id})"
                    if provenance.software.toetra_build_id is not None
                    else ""
                ),
                resolved,
            )
        )
        if provenance.unavailable_inputs:
            lines.extend(
                _indented_wrapped(
                    "Unavailable inputs: " + ", ".join(provenance.unavailable_inputs),
                    resolved,
                )
            )

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


def _render_point_groups(
    report: VerificationReport,
    options: TextRenderOptions,
) -> list[str]:
    lines: list[str] = []
    for point in report.points:
        if not point.inputs and not point.outputs:
            continue
        lines.append(f"  Point {point.name} ({point.binding_kind})")
        if point.provenance:
            lines.append(f"    provenance = {point.provenance}")
        for assignment in point.inputs + point.outputs:
            lines.extend(_render_assignment(assignment, options))
    if report.auxiliary_assignments:
        lines.append("  Auxiliary values")
        for assignment in report.auxiliary_assignments:
            lines.extend(_render_assignment(assignment, options))
    return lines


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


def _render_model_evaluations(
    report: VerificationReport,
    options: TextRenderOptions,
) -> list[str]:
    lines: list[str] = []
    for evaluation in report.model_evaluations:
        lines.append(
            f"  Point {evaluation.point_name} · output {evaluation.output_name}"
        )
        if evaluation.native_probability_threshold is not None:
            lines.append(
                "    native decision: probability > "
                f"{evaluation.native_probability_threshold}; decision value > "
                f"{evaluation.native_decision_threshold}; equality -> "
                f"{evaluation.equality_label!r}"
            )
        if evaluation.predicted_label is not None:
            lines.append(f"    predicted label = {evaluation.predicted_label!r}")
        for probability in evaluation.probabilities:
            lines.append(
                "    reconstructed probability"
                f"({probability.label!r}) = {probability.value} "
                f"({probability.precision_digits} digits; "
                f"source={probability.source})"
            )
        for quantity in evaluation.quantities:
            lines.append(f"    technical {quantity.kind} = {quantity.value}")
        for lowering in evaluation.lowerings:
            if lowering.related_point_name is not None:
                intent = f"predicted_label[{evaluation.point_name}] {lowering.operator} predicted_label[{lowering.related_point_name}]"
            else:
                intent = (
                    f"{lowering.observable}({lowering.label!r})"
                    if lowering.observable == "class_probability"
                    else f"{lowering.observable} == {lowering.label!r}"
                )
                if lowering.property_threshold is not None:
                    intent = f"{lowering.observable}({lowering.label!r}) {lowering.operator} {lowering.property_threshold}"
            lines.append(f"    intent: {intent}")
            lines.append(
                "      trace: "
                f"semantic={lowering.semantic_profile_id}@"
                f"{lowering.semantic_profile_version}; "
                f"transformation={lowering.transformation_id}@"
                f"{lowering.transformation_version}; "
                f"polarity={lowering.logical_polarity}"
            )
            if lowering.canonical_formula_kind is not None:
                lines.append(
                    f"      lowering: {lowering.canonical_formula_kind} at {lowering.quantity_kind} threshold {lowering.canonical_threshold}"
                )
            else:
                lines.append(
                    f"      lowering: {lowering.quantity_kind} {lowering.canonical_operator} {lowering.canonical_threshold}"
                )
            if lowering.exact_threshold_expression is not None:
                precision = _format_threshold_precision(lowering)
                lines.append(
                    "      threshold: "
                    f"{lowering.exact_threshold_expression} in "
                    f"[{lowering.threshold_lower_bound}, "
                    f"{lowering.threshold_upper_bound}] "
                    f"(selected {lowering.selected_bound}{precision})"
                )
            if lowering.property_value is not None:
                related = (
                    f"; related[{lowering.related_point_name}]={lowering.related_property_value}"
                    if lowering.related_point_name is not None
                    else ""
                )
                lines.append(
                    "      observed: "
                    f"{lowering.property_value}{related}; satisfied={lowering.property_satisfied}; margin={lowering.property_margin}"
                )
            if lowering.quantity_value is not None:
                related = (
                    f"; related[{lowering.related_point_name}]={lowering.related_quantity_value}"
                    if lowering.related_point_name is not None
                    else ""
                )
                lines.append(
                    "      canonical value: "
                    f"{lowering.quantity_value}{related}; margin={lowering.canonical_margin}"
                )
            lines.append(
                "      compatibility: "
                f"{lowering.compatibility_classification}; conclusions="
                + ", ".join(lowering.permitted_conclusions)
            )
    return lines


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


def _format_backend_options(
    options: Mapping[str, bool | int | float | str],
) -> str:
    rendered = ", ".join(f"{key}={value!r}" for key, value in options.items())
    return rendered or "none"


def _format_threshold_precision(lowering: ReportLoweringTrace) -> str:
    values = (
        ("precision", lowering.precision_digits),
        ("working", lowering.working_precision_digits),
        ("guard", lowering.guard_digits),
    )
    rendered = ", ".join(
        f"{name}={value}" for name, value in values if value is not None
    )
    return f"; {rendered}" if rendered else ""
