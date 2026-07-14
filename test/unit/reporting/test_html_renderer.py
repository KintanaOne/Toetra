from __future__ import annotations

from pathlib import Path

from dsl.backends.diagnostics import (
    BackendDiagnosticSeverity,
    BackendResultDiagnostic,
)
from dsl.backends.results import VerificationStatus
from dsl.ir.ir2.enums import VerificationSemantics
from dsl.language.vocabulary.backends import EnumBackend
from dsl.language.vocabulary.properties import EnumProperty
from dsl.reporting import (
    HtmlRenderOptions,
    ReportAssignment,
    ReportAssignmentKind,
    ReportScope,
    ReportScopeVariable,
    VerificationReport,
    render_verification_reports_html,
)


def _report(
    *,
    status: VerificationStatus = VerificationStatus.COUNTEREXAMPLE,
    property_index: int = 0,
) -> VerificationReport:
    return VerificationReport(
        property_index=property_index,
        property_type=EnumProperty.LOGIC,
        semantics=VerificationSemantics.REFUTATION,
        scope=ReportScope(
            kind="quantifier",
            quantifier="forall",
            variables=(ReportScopeVariable(name="applicant", role="bound"),),
        ),
        specification="_model.score < 7.0 and label != '<script>'",
        backend=EnumBackend.Z3,
        backend_status="sat",
        status=status,
        summary="Property violated <strong>without trusted markup</strong>.",
        assignments=(
            ReportAssignment(
                raw_name="applicant.ratio",
                display_name="applicant.ratio",
                value="1/3",
                kind=ReportAssignmentKind.INPUT,
            ),
            ReportAssignment(
                raw_name="_model.score",
                display_name="score",
                value=7,
                kind=ReportAssignmentKind.OUTPUT,
            ),
        ),
        diagnostics=(
            BackendResultDiagnostic(
                code="EXAMPLE<script>",
                severity=BackendDiagnosticSeverity.WARNING,
                message="Diagnostic <em>content</em> is escaped.",
            ),
        ),
        assumption_count=3,
        route_reason="requested backend satisfies IR2 requirements",
    )


def test_html_renderer_builds_accessible_counterexample_card() -> None:
    rendered = _report().to_html()

    assert 'class="forml-report-root"' in rendered
    assert 'aria-label="FORML property 1"' in rendered
    assert 'class="forml-badge failure">Counterexample</span>' in rendered
    assert "Counterexample" in rendered
    assert "Inputs" in rendered
    assert "applicant.ratio" in rendered
    assert "Model outputs" in rendered
    assert "score" in rendered
    assert "requested backend satisfies IR2 requirements" in rendered


def test_html_renderer_escapes_all_user_and_backend_text() -> None:
    rendered = _report().to_html()

    assert "<script>" not in rendered
    assert "<strong>without trusted markup</strong>" not in rendered
    assert "<em>content</em>" not in rendered
    assert "&lt;script&gt;" in rendered
    assert "&lt;strong&gt;without trusted markup&lt;/strong&gt;" in rendered
    assert "&lt;em&gt;content&lt;/em&gt;" in rendered


def test_html_collection_summarizes_statuses_without_duplicate_styles() -> None:
    rendered = render_verification_reports_html(
        (
            _report(status=VerificationStatus.PROVED, property_index=0),
            _report(status=VerificationStatus.COUNTEREXAMPLE, property_index=1),
            _report(status=VerificationStatus.WITNESS, property_index=2),
        ),
        options=HtmlRenderOptions(collection_title="Credit risk validation"),
    )

    assert rendered.count("<style>") == 1
    assert "Credit risk validation" in rendered
    assert "Proved: 1" in rendered
    assert "Counterexample: 1" in rendered
    assert "Witness: 1" in rendered


def test_html_writer_creates_standalone_document(tmp_path: Path) -> None:
    output = _report().write_html(tmp_path / "reports" / "property.html")
    written = output.read_text(encoding="utf-8")

    assert written.startswith("<!doctype html>")
    assert '<meta charset="utf-8">' in written
    assert "FORML Verification Report" in written
    assert written.endswith("</html>\n")
