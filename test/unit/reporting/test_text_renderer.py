from __future__ import annotations

from toetra._backends.diagnostics import (
    BackendDiagnosticSeverity,
    BackendResultDiagnostic,
)
from toetra._backends.results import VerificationStatus
from toetra._compiler.ir.ir2.enums import VerificationSemantics
from toetra._language.vocabulary.backends import EnumBackend
from toetra._language.vocabulary.properties import EnumProperty
from toetra._reporting.model import (
    ReportAssignment,
    ReportAssignmentKind,
    ReportScope,
    ReportScopeVariable,
    VerificationReport,
)
from toetra._reporting.text import (
    TextRenderOptions,
    render_verification_reports_text,
)


def _report(
    *,
    status: VerificationStatus = VerificationStatus.COUNTEREXAMPLE,
) -> VerificationReport:
    return VerificationReport(
        property_index=1,
        property_type=EnumProperty.LOGIC,
        semantics=VerificationSemantics.REFUTATION,
        scope=ReportScope(
            kind="quantifier",
            quantifier="forall",
            variables=(ReportScopeVariable(name="x0", role="bound"),),
        ),
        specification="_model.score < 7.0",
        backend=EnumBackend.Z3,
        backend_status="sat",
        status=status,
        summary="Property violated under the encoded assumptions.",
        assignments=(
            ReportAssignment(
                raw_name="x0.a",
                display_name="x0.a",
                value=3,
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
                code="EXAMPLE_WARNING",
                severity=BackendDiagnosticSeverity.WARNING,
                message="The example diagnostic remains visible to the user.",
            ),
        ),
        assumption_count=3,
        route_reason="requested backend satisfies IR2 requirements",
    )


def test_text_renderer_groups_counterexample_assignments() -> None:
    rendered = _report().to_text()

    assert "Toetra Verification Report · Property 2" in rendered
    assert "✗ COUNTEREXAMPLE" in rendered
    assert "Scope         : forall x0" in rendered
    assert "Counterexample" in rendered
    assert "Inputs" in rendered
    assert "x0.a = 3" in rendered
    assert "Model outputs" in rendered
    assert "score = 7" in rendered
    assert "[WARNING] EXAMPLE_WARNING" in rendered


def test_text_renderer_supports_ascii_output_and_hidden_route() -> None:
    options = TextRenderOptions(
        width=60,
        use_unicode=False,
        include_route_reason=False,
    )

    rendered = render_verification_reports_text((_report(),), options=options)

    assert "=" * 60 in rendered
    assert "FAIL COUNTEREXAMPLE" in rendered
    assert "Route" not in rendered
    assert "━" not in rendered


def test_text_renderer_labels_existential_assignment_as_witness() -> None:
    report = _report(status=VerificationStatus.WITNESS)

    rendered = report.to_text()

    assert "✓ WITNESS" in rendered
    assert "Witness" in rendered


def test_text_renderer_rejects_too_narrow_output() -> None:
    try:
        TextRenderOptions(width=40)
    except ValueError as error:
        assert "at least 48" in str(error)
    else:
        raise AssertionError("Expected narrow text report width to be rejected")
