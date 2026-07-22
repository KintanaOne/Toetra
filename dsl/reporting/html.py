from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any

from dsl.backends.diagnostics import BackendResultDiagnostic
from dsl.backends.results import VerificationStatus
from dsl.reporting.model import ReportAssignment, VerificationReport


@dataclass(frozen=True)
class HtmlRenderOptions:
    """Configuration shared by notebook and standalone HTML renderers."""

    include_route_reason: bool = True
    include_inline_styles: bool = True
    collection_title: str = "FORML Verification Session"
    collection_subtitle: str | None = None


_STATUS_LABELS = {
    VerificationStatus.PROVED: "Proved",
    VerificationStatus.COUNTEREXAMPLE: "Counterexample",
    VerificationStatus.WITNESS: "Witness",
    VerificationStatus.NO_WITNESS: "No witness",
    VerificationStatus.UNKNOWN: "Unknown",
}

_STATUS_CLASSES = {
    VerificationStatus.PROVED: "success",
    VerificationStatus.COUNTEREXAMPLE: "failure",
    VerificationStatus.WITNESS: "success",
    VerificationStatus.NO_WITNESS: "warning",
    VerificationStatus.UNKNOWN: "neutral",
}

_STYLES = """
.forml-report-root {
  --forml-bg: #ffffff;
  --forml-surface: #f8fafc;
  --forml-border: #dbe3ee;
  --forml-text: #172033;
  --forml-muted: #5d6b82;
  --forml-accent: #4f46e5;
  --forml-success: #087f5b;
  --forml-success-bg: #e9fbf4;
  --forml-failure: #b42318;
  --forml-failure-bg: #fff0ee;
  --forml-warning: #a15c00;
  --forml-warning-bg: #fff7e8;
  --forml-neutral: #475467;
  --forml-neutral-bg: #f2f4f7;
  color: var(--forml-text);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
    "Segoe UI", sans-serif;
  line-height: 1.45;
}
.forml-report-root * { box-sizing: border-box; }
.forml-session-header {
  margin: 0 0 1rem;
  padding: 1rem 1.1rem;
  border: 1px solid var(--forml-border);
  border-radius: 14px;
  background: linear-gradient(135deg, #f7f8ff, #ffffff);
}
.forml-session-header h2 { margin: 0; font-size: 1.15rem; }
.forml-session-header p { margin: .35rem 0 0; color: var(--forml-muted); }
.forml-session-counts { display: flex; flex-wrap: wrap; gap: .45rem; margin-top: .75rem; }
.forml-count {
  border: 1px solid var(--forml-border);
  border-radius: 999px;
  background: var(--forml-bg);
  padding: .2rem .6rem;
  font-size: .8rem;
}
.forml-report-card {
  overflow: hidden;
  margin: 0 0 1rem;
  border: 1px solid var(--forml-border);
  border-radius: 14px;
  background: var(--forml-bg);
  box-shadow: 0 6px 20px rgba(23, 32, 51, .06);
}
.forml-report-card header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 1.1rem;
  border-bottom: 1px solid var(--forml-border);
  background: var(--forml-surface);
}
.forml-report-card h3 { margin: 0; font-size: 1.05rem; }
.forml-kicker { margin: 0 0 .2rem; color: var(--forml-muted); font-size: .78rem; text-transform: uppercase; letter-spacing: .04em; }
.forml-badge { display: inline-flex; align-items: center; border-radius: 999px; padding: .3rem .68rem; font-size: .78rem; font-weight: 700; white-space: nowrap; }
.forml-badge.success { color: var(--forml-success); background: var(--forml-success-bg); }
.forml-badge.failure { color: var(--forml-failure); background: var(--forml-failure-bg); }
.forml-badge.warning { color: var(--forml-warning); background: var(--forml-warning-bg); }
.forml-badge.neutral { color: var(--forml-neutral); background: var(--forml-neutral-bg); }
.forml-report-body { padding: 1rem 1.1rem 1.1rem; }
.forml-summary { margin: 0 0 1rem; font-size: .95rem; }
.forml-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: .65rem;
  margin: 0 0 1rem;
}
.forml-meta div { padding: .65rem .75rem; border-radius: 10px; background: var(--forml-surface); }
.forml-meta dt { margin: 0 0 .15rem; color: var(--forml-muted); font-size: .72rem; text-transform: uppercase; letter-spacing: .04em; }
.forml-meta dd { margin: 0; font-weight: 600; overflow-wrap: anywhere; }
.forml-section { margin-top: 1rem; }
.forml-section h4 { margin: 0 0 .5rem; font-size: .88rem; }
.forml-specification {
  display: block;
  overflow-x: auto;
  padding: .7rem .8rem;
  border: 1px solid var(--forml-border);
  border-radius: 10px;
  background: #111827;
  color: #f8fafc;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: .84rem;
  white-space: pre-wrap;
}
.forml-assignment-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: .75rem; }
.forml-assignment-group { border: 1px solid var(--forml-border); border-radius: 10px; overflow: hidden; }
.forml-assignment-group h5 { margin: 0; padding: .55rem .7rem; background: var(--forml-surface); font-size: .8rem; }
.forml-assignment-group table { width: 100%; border-collapse: collapse; font-size: .82rem; }
.forml-assignment-group th, .forml-assignment-group td { padding: .48rem .7rem; border-top: 1px solid var(--forml-border); text-align: left; vertical-align: top; overflow-wrap: anywhere; }
.forml-assignment-group th { width: 48%; color: var(--forml-muted); font-weight: 600; }
.forml-diagnostics { margin: .25rem 0 0; padding: 0; list-style: none; }
.forml-diagnostic { margin-top: .45rem; padding: .65rem .75rem; border-left: 4px solid var(--forml-warning); border-radius: 8px; background: var(--forml-warning-bg); }
.forml-diagnostic strong { display: block; font-size: .8rem; }
.forml-diagnostic span { color: var(--forml-muted); font-size: .82rem; }
.forml-route { margin-top: .75rem; color: var(--forml-muted); font-size: .78rem; }
@media (prefers-color-scheme: dark) {
  .forml-report-root {
    --forml-bg: #111827;
    --forml-surface: #182234;
    --forml-border: #344054;
    --forml-text: #f8fafc;
    --forml-muted: #b8c2d1;
    --forml-success-bg: #0c3b2e;
    --forml-failure-bg: #4a1d1a;
    --forml-warning-bg: #46310d;
    --forml-neutral-bg: #273244;
  }
  .forml-session-header { background: linear-gradient(135deg, #1d2345, #111827); }
  .forml-specification { background: #0b1020; }
}
""".strip()


def render_verification_report_html(
    report: VerificationReport,
    *,
    options: HtmlRenderOptions | None = None,
) -> str:
    """Render one backend-neutral report as a notebook-safe HTML fragment."""

    resolved = options or HtmlRenderOptions()
    styles = _style_block() if resolved.include_inline_styles else ""
    return (
        styles
        + '<div class="forml-report-root">'
        + _render_report_card(report, resolved)
        + "</div>"
    )


def render_verification_reports_html(
    reports: Iterable[VerificationReport],
    *,
    options: HtmlRenderOptions | None = None,
) -> str:
    """Render a report collection with a compact visual summary."""

    resolved = options or HtmlRenderOptions()
    report_items = tuple(reports)
    styles = _style_block() if resolved.include_inline_styles else ""
    cards = "".join(_render_report_card(report, resolved) for report in report_items)
    return (
        styles
        + '<div class="forml-report-root">'
        + _render_collection_header(report_items, resolved)
        + cards
        + "</div>"
    )


def write_verification_report_html(
    report: VerificationReport,
    path: str | Path,
    *,
    options: HtmlRenderOptions | None = None,
) -> Path:
    """Write one report as a self-contained HTML document."""

    resolved = options or HtmlRenderOptions()
    body = (
        '<div class="forml-report-root">'
        + _render_report_card(report, resolved)
        + "</div>"
    )
    return _write_html(path, _standalone_document("FORML Verification Report", body))


def write_verification_reports_html(
    reports: Iterable[VerificationReport],
    path: str | Path,
    *,
    options: HtmlRenderOptions | None = None,
) -> Path:
    """Write several reports as one self-contained HTML document."""

    resolved = options or HtmlRenderOptions()
    report_items = tuple(reports)
    body = (
        '<div class="forml-report-root">'
        + _render_collection_header(report_items, resolved)
        + "".join(_render_report_card(report, resolved) for report in report_items)
        + "</div>"
    )
    return _write_html(path, _standalone_document(resolved.collection_title, body))


def _render_collection_header(
    reports: tuple[VerificationReport, ...],
    options: HtmlRenderOptions,
) -> str:
    counts = Counter(report.status for report in reports)
    count_items = "".join(
        '<span class="forml-count">'
        f"{escape(_STATUS_LABELS[status])}: {counts[status]}"
        "</span>"
        for status in VerificationStatus
        if counts[status]
    )
    subtitle = (
        f"<p>{escape(options.collection_subtitle)}</p>"
        if options.collection_subtitle
        else ""
    )
    return (
        '<div class="forml-session-header">'
        f"<h2>{escape(options.collection_title)}</h2>"
        + subtitle
        + f'<div class="forml-session-counts">{count_items}</div>'
        + "</div>"
    )


def _render_report_card(
    report: VerificationReport,
    options: HtmlRenderOptions,
) -> str:
    status_class = _STATUS_CLASSES[report.status]
    scope = _format_scope(report)
    assignments = _render_assignments(report)
    model_evaluations = _render_model_evaluations(report)
    numeric_compatibility = _render_numeric_compatibility(report)
    backend_execution = _render_backend_execution(report)
    provenance = _render_provenance(report)
    diagnostics = _render_diagnostics(report.diagnostics)
    route = (
        f'<p class="forml-route"><strong>Route:</strong> {escape(report.route_reason)}</p>'
        if options.include_route_reason
        else ""
    )
    return (
        f'<section class="forml-report-card" aria-label="FORML property {report.property_index + 1}">'
        "<header>"
        "<div>"
        f'<p class="forml-kicker">Property {report.property_index + 1}</p>'
        f"<h3>{escape(report.property_type.value)}</h3>"
        "</div>"
        f'<span class="forml-badge {status_class}">{escape(_STATUS_LABELS[report.status])}</span>'
        "</header>"
        '<div class="forml-report-body">'
        f'<p class="forml-summary">{escape(report.summary or "No summary was provided.")}</p>'
        '<dl class="forml-meta">'
        + _meta_item("Semantics", report.semantics.value)
        + _meta_item("Scope", scope)
        + _meta_item("Backend", f"{report.backend.value} · {report.backend_status}")
        + _meta_item("Assumptions", str(report.assumption_count))
        + (
            _meta_item(
                "Verification",
                report.provenance.verification_fingerprint.split(":", 1)[-1][:12],
            )
            if report.provenance is not None
            else ""
        )
        + (
            _meta_item("Provenance", report.provenance.completeness.value)
            if report.provenance is not None
            else ""
        )
        + (
            _meta_item(
                "Numeric guarantee",
                report.numeric_compatibility.classification,
            )
            if report.numeric_compatibility is not None
            else ""
        )
        + (
            _meta_item(
                "Claim scope",
                report.numeric_compatibility.conclusion_scope,
            )
            if report.numeric_compatibility is not None
            else ""
        )
        + "</dl>"
        '<div class="forml-section">'
        "<h4>Specification</h4>"
        f'<code class="forml-specification">{escape(report.specification)}</code>'
        "</div>"
        + backend_execution
        + numeric_compatibility
        + provenance
        + model_evaluations
        + assignments
        + diagnostics
        + route
        + "</div>"
        + "</section>"
    )


def _meta_item(label: str, value: str) -> str:
    return f"<div><dt>{escape(label)}</dt><dd>{escape(value)}</dd></div>"


def _format_scope(report: VerificationReport) -> str:
    variable_names = ", ".join(variable.name for variable in report.scope.variables)
    if report.scope.quantifier:
        return " ".join(
            part for part in (report.scope.quantifier, variable_names) if part
        )
    if variable_names:
        return f"{report.scope.kind} {variable_names}"
    return report.scope.kind


def _render_backend_execution(report: VerificationReport) -> str:
    execution = report.backend_execution
    if execution is None:
        return ""

    timeout = (
        "disabled" if execution.timeout_ms is None else f"{execution.timeout_ms} ms"
    )
    rows = (
        ("Status", execution.status),
        ("Duration", f"{execution.duration_ms:.3f} ms"),
        ("Timeout", timeout),
        (
            "Backend units",
            (
                str(execution.max_backend_units)
                if execution.max_backend_units is not None
                else "unbounded"
            ),
        ),
        (
            "Memory",
            (
                f"{execution.max_memory_mb} MB"
                if execution.max_memory_mb is not None
                else "unbounded"
            ),
        ),
        (
            "Deterministic seed",
            (
                str(execution.deterministic_seed)
                if execution.deterministic_seed is not None
                else "default"
            ),
        ),
        ("Reason", execution.reason or "—"),
        ("Backend reason", execution.backend_reason or "—"),
    )
    table_rows = "".join(
        f"<tr><th>{escape(label)}</th><td>{escape(value)}</td></tr>"
        for label, value in rows
    )
    return (
        '<div class="forml-section">'
        "<h4>Backend execution</h4>"
        '<div class="forml-assignment-group">'
        f"<table><tbody>{table_rows}</tbody></table>"
        "</div></div>"
    )


def _render_numeric_compatibility(report: VerificationReport) -> str:
    compatibility = report.numeric_compatibility
    if compatibility is None:
        return ""

    requirements = ", ".join(compatibility.property_numeric_requirements) or "None"
    permitted = ", ".join(compatibility.permitted_conclusions) or "None"
    replay = ", ".join(compatibility.replay_required_for) or "None"
    rule_id = compatibility.matched_rule_id or "<no matching rule>"

    rows = (
        ("Rule", rule_id),
        ("Support", compatibility.support_status),
        ("Classification", compatibility.classification),
        ("Semantic target", compatibility.semantic_target),
        ("Conclusion scope", compatibility.conclusion_scope),
        ("Source route", compatibility.source_route),
        (
            "Encoder",
            f"{compatibility.model_encoder_id}@{compatibility.model_encoder_version}",
        ),
        ("Backend route", compatibility.backend_route),
        ("Property requirements", requirements),
        ("Permitted conclusions", permitted),
        ("Replay required for", replay),
    )
    table_rows = "".join(
        f"<tr><th>{escape(label)}</th><td>{escape(value)}</td></tr>"
        for label, value in rows
    )

    notes = ""
    note_items = tuple(compatibility.assumptions_and_preconditions) + tuple(
        compatibility.compatibility_diagnostics
    )
    if note_items:
        notes = (
            '<ul class="forml-diagnostics">'
            + "".join(
                '<li class="forml-diagnostic"><span>' + escape(item) + "</span></li>"
                for item in note_items
            )
            + "</ul>"
        )

    return (
        '<div class="forml-section">'
        "<h4>Numeric compatibility</h4>"
        '<div class="forml-assignment-group">'
        f"<table><tbody>{table_rows}</tbody></table>"
        "</div>" + notes + "</div>"
    )


def _render_provenance(report: VerificationReport) -> str:
    provenance = report.provenance
    if provenance is None:
        return ""

    rows = (
        ("Captured", provenance.captured_at_utc),
        ("Completeness", provenance.completeness.value),
        ("Inputs", provenance.input_fingerprint),
        ("Property", provenance.property_fingerprint),
        ("Route", provenance.route_fingerprint),
        ("Execution policy", provenance.execution_policy_fingerprint),
        ("Verification", provenance.verification_fingerprint),
        ("FORML version", provenance.software.forml_version),
        ("FORML build", provenance.software.forml_build_id or "unavailable"),
        (
            "Compiler",
            f"{provenance.compiler.actual_normal_form} / "
            f"strict={provenance.compiler.strict}",
        ),
    )
    table_rows = "".join(
        f"<tr><th>{escape(label)}</th><td>{escape(value)}</td></tr>"
        for label, value in rows
    )
    unavailable = ""
    if provenance.unavailable_inputs:
        unavailable = (
            '<p class="forml-route"><strong>Unavailable inputs:</strong> '
            + escape(", ".join(provenance.unavailable_inputs))
            + "</p>"
        )
    return (
        '<div class="forml-section">'
        "<h4>Verification provenance</h4>"
        '<div class="forml-assignment-group">'
        f"<table><tbody>{table_rows}</tbody></table>"
        "</div>" + unavailable + "</div>"
    )


def _render_model_evaluations(report: VerificationReport) -> str:
    if not report.model_evaluations:
        return ""

    groups: list[str] = []
    for evaluation in report.model_evaluations:
        rows: list[tuple[str, str]] = []
        if evaluation.native_probability_threshold is not None:
            rows.extend(
                [
                    (
                        "Native probability threshold",
                        evaluation.native_probability_threshold,
                    ),
                    (
                        "Native decision threshold",
                        evaluation.native_decision_threshold or "—",
                    ),
                    ("Boundary label", repr(evaluation.equality_label)),
                ]
            )
        if evaluation.predicted_label is not None:
            rows.append(("Predicted label", repr(evaluation.predicted_label)))
        rows.extend(
            (
                f"Reconstructed probability {item.label!r}",
                f"{item.value} ({item.precision_digits} digits)",
            )
            for item in evaluation.probabilities
        )
        rows.extend(
            (f"Technical {item.kind}", str(item.value))
            for item in evaluation.quantities
        )
        for index, lowering in enumerate(evaluation.lowerings, start=1):
            if lowering.related_point_name is not None:
                intent = f"predicted_label[{evaluation.point_name}] {lowering.operator} predicted_label[{lowering.related_point_name}]"
                lowering_text = f"{lowering.canonical_formula_kind} at {lowering.quantity_kind} threshold {lowering.canonical_threshold}"
            else:
                intent = (
                    f"{lowering.observable}({lowering.label!r}) {lowering.operator} {lowering.property_threshold}"
                    if lowering.property_threshold is not None
                    else f"{lowering.observable} {lowering.operator} {lowering.label!r}"
                )
                lowering_text = f"{lowering.quantity_kind} {lowering.canonical_operator} {lowering.canonical_threshold}"
            rows.extend(
                [
                    (f"Intent {index}", intent),
                    (f"Lowering {index}", lowering_text),
                    (
                        f"Observed {index}",
                        f"value={lowering.property_value}; satisfied={lowering.property_satisfied}; margin={lowering.property_margin}",
                    ),
                    (
                        f"Canonical {index}",
                        f"value={lowering.quantity_value}; margin={lowering.canonical_margin}; compatibility={lowering.compatibility_classification}",
                    ),
                ]
            )
            if lowering.related_point_name is not None:
                rows.append(
                    (
                        f"Related {index}",
                        f"point={lowering.related_point_name}; label={lowering.related_property_value}; quantity={lowering.related_quantity_value}",
                    )
                )
            if lowering.exact_threshold_expression is not None:
                rows.append(
                    (
                        f"Threshold evidence {index}",
                        f"{lowering.exact_threshold_expression} in [{lowering.threshold_lower_bound}, {lowering.threshold_upper_bound}], selected {lowering.selected_bound}",
                    )
                )
        table_rows = "".join(
            f"<tr><th>{escape(label)}</th><td><code>{escape(value)}</code></td></tr>"
            for label, value in rows
        )
        groups.append(
            '<div class="forml-assignment-group">'
            f"<h5>Point {escape(evaluation.point_name)} · "
            f"{escape(evaluation.output_name)}</h5>"
            f"<table><tbody>{table_rows}</tbody></table>"
            "</div>"
        )
    return (
        '<div class="forml-section">'
        "<h4>Model evaluations</h4>"
        f'<div class="forml-assignment-grid">{"".join(groups)}</div>'
        "</div>"
    )


def _render_assignments(report: VerificationReport) -> str:
    if report.points:
        rendered = "".join(
            _render_assignment_group(
                f"Point {point.name} · {point.binding_kind}",
                point.inputs + point.outputs,
            )
            for point in report.points
            if point.inputs or point.outputs
        )
        if report.auxiliary_assignments:
            rendered += _render_assignment_group(
                "Auxiliary values", report.auxiliary_assignments
            )
    else:
        groups = (
            ("Inputs", report.inputs),
            ("Model outputs", report.outputs),
            ("Auxiliary values", report.auxiliary_assignments),
        )
        rendered = "".join(
            _render_assignment_group(label, assignments)
            for label, assignments in groups
            if assignments
        )
    if not rendered:
        return ""
    title = (
        "Counterexample"
        if report.status is VerificationStatus.COUNTEREXAMPLE
        else (
            "Witness"
            if report.status is VerificationStatus.WITNESS
            else "Backend assignments"
        )
    )
    return (
        '<div class="forml-section">'
        f"<h4>{escape(title)}</h4>"
        f'<div class="forml-assignment-grid">{rendered}</div>'
        "</div>"
    )


def _render_assignment_group(
    label: str,
    assignments: tuple[ReportAssignment, ...],
) -> str:
    rows = "".join(
        "<tr>"
        f"<th>{escape(assignment.display_name)}</th>"
        f"<td><code>{escape(_format_value(assignment.value))}</code></td>"
        "</tr>"
        for assignment in assignments
    )
    return (
        '<div class="forml-assignment-group">'
        f"<h5>{escape(label)}</h5>"
        f"<table><tbody>{rows}</tbody></table>"
        "</div>"
    )


def _render_diagnostics(
    diagnostics: tuple[BackendResultDiagnostic, ...],
) -> str:
    if not diagnostics:
        return ""
    items = "".join(
        '<li class="forml-diagnostic">'
        f"<strong>{escape(diagnostic.severity.value.upper())} · {escape(diagnostic.code)}</strong>"
        f"<span>{escape(diagnostic.message)}</span>"
        "</li>"
        for diagnostic in diagnostics
    )
    return (
        '<div class="forml-section">'
        "<h4>Diagnostics</h4>"
        f'<ul class="forml-diagnostics">{items}</ul>'
        "</div>"
    )


def _format_value(value: Any) -> str:
    return str(value)


def _style_block() -> str:
    return f"<style>{_STYLES}</style>"


def _standalone_document(title: str, body: str) -> str:
    return (
        "<!doctype html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{escape(title)}</title>\n"
        f"<style>{_STYLES}</style>\n"
        "</head>\n"
        f"<body>{body}</body>\n"
        "</html>\n"
    )


def _write_html(path: str | Path, content: str) -> Path:
    output = Path(path).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    return output
