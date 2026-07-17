"""User-facing verification report models, renderers and serializers."""

from dsl.reporting.builder import build_verification_report
from dsl.reporting.html import (
    HtmlRenderOptions,
    render_verification_report_html,
    render_verification_reports_html,
    write_verification_report_html,
    write_verification_reports_html,
)
from dsl.reporting.json import (
    REPORT_COLLECTION_SCHEMA,
    REPORT_SCHEMA,
    REPORT_SCHEMA_VERSION,
    verification_report_to_dict,
    verification_report_to_json,
    verification_reports_to_dict,
    verification_reports_to_json,
    write_verification_report_json,
    write_verification_reports_json,
)
from dsl.reporting.model import (
    ReportAssignment,
    ReportAssignmentKind,
    ReportPointEvidence,
    ReportScope,
    ReportScopeVariable,
    VerificationReport,
)
from dsl.reporting.text import (
    TextRenderOptions,
    render_verification_report_text,
    render_verification_reports_text,
)

__all__ = [
    "REPORT_COLLECTION_SCHEMA",
    "REPORT_SCHEMA",
    "REPORT_SCHEMA_VERSION",
    "HtmlRenderOptions",
    "ReportAssignment",
    "ReportAssignmentKind",
    "ReportPointEvidence",
    "ReportScope",
    "ReportScopeVariable",
    "TextRenderOptions",
    "VerificationReport",
    "build_verification_report",
    "render_verification_report_html",
    "render_verification_report_text",
    "render_verification_reports_html",
    "render_verification_reports_text",
    "verification_report_to_dict",
    "verification_report_to_json",
    "verification_reports_to_dict",
    "verification_reports_to_json",
    "write_verification_report_html",
    "write_verification_report_json",
    "write_verification_reports_html",
    "write_verification_reports_json",
]
