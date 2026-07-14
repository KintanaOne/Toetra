from __future__ import annotations

import json
from pathlib import Path
from fractions import Fraction

import z3

from dsl.backends.diagnostics import (
    BackendDiagnosticSeverity,
    BackendResultDiagnostic,
)
from dsl.backends.results import VerificationStatus
from dsl.ir.ir2.enums import VerificationSemantics
from dsl.language.vocabulary.backends import EnumBackend
from dsl.language.vocabulary.properties import EnumProperty
from dsl.reporting import (
    REPORT_COLLECTION_SCHEMA,
    REPORT_SCHEMA,
    REPORT_SCHEMA_VERSION,
    ReportAssignment,
    ReportAssignmentKind,
    ReportScope,
    ReportScopeVariable,
    VerificationReport,
    verification_reports_to_dict,
    write_verification_reports_json,
)


def _report() -> VerificationReport:
    return VerificationReport(
        property_index=0,
        property_type=EnumProperty.BOUND,
        semantics=VerificationSemantics.REFUTATION,
        scope=ReportScope(
            kind="quantifier",
            quantifier="forall",
            variables=(ReportScopeVariable(name="x0", role="bound"),),
        ),
        specification="_model.score <= 7.0",
        backend=EnumBackend.Z3,
        backend_status="sat",
        status=VerificationStatus.COUNTEREXAMPLE,
        summary="Property violated",
        assignments=(
            ReportAssignment(
                raw_name="x0.a",
                display_name="x0.a",
                value=z3.IntVal(3),
                kind=ReportAssignmentKind.INPUT,
            ),
            ReportAssignment(
                raw_name="_model.score",
                display_name="score",
                value=z3.RealVal("5/2"),
                kind=ReportAssignmentKind.OUTPUT,
            ),
            ReportAssignment(
                raw_name="ratio",
                display_name="ratio",
                value=Fraction(1, 3),
                kind=ReportAssignmentKind.AUXILIARY,
            ),
        ),
        diagnostics=(
            BackendResultDiagnostic(
                code="EXAMPLE",
                severity=BackendDiagnosticSeverity.INFO,
                message="example",
            ),
        ),
        assumption_count=2,
        route_reason="requested backend satisfies IR2 requirements",
    )


def test_report_to_dict_uses_versioned_stable_contract() -> None:
    payload = _report().to_dict()

    assert payload["schema"] == REPORT_SCHEMA
    assert payload["schema_version"] == REPORT_SCHEMA_VERSION
    assert payload["property"] == {
        "index": 0,
        "type": "BOUND",
        "semantics": "refutation",
        "specification": "_model.score <= 7.0",
    }
    assert payload["execution"]["status"] == "counterexample"
    assert payload["scope"]["variables"] == [{"name": "x0", "role": "bound"}]
    assert payload["assignments"]["inputs"][0]["value"] == 3
    assert payload["assignments"]["outputs"][0]["value"] == {
        "kind": "rational",
        "numerator": 5,
        "denominator": 2,
        "text": "5/2",
    }
    assert payload["assignments"]["auxiliary"][0]["value"] == {
        "kind": "rational",
        "numerator": 1,
        "denominator": 3,
        "text": "1/3",
    }
    assert payload["diagnostics"] == [
        {"code": "EXAMPLE", "severity": "info", "message": "example"}
    ]


def test_report_to_json_is_valid_utf8_json() -> None:
    payload = json.loads(_report().to_json())

    assert payload["schema"] == REPORT_SCHEMA
    assert payload["assignments"]["outputs"][0]["name"] == "score"


def test_report_write_json_creates_parent_directories(tmp_path) -> None:
    output = _report().write_json(tmp_path / "reports" / "property-1.json")

    assert output.exists()
    assert json.loads(output.read_text(encoding="utf-8"))["schema"] == REPORT_SCHEMA


def test_report_collection_contract_and_writer(tmp_path) -> None:
    report = _report()
    payload = verification_reports_to_dict((report, report))

    assert payload["schema"] == REPORT_COLLECTION_SCHEMA
    assert payload["schema_version"] == REPORT_SCHEMA_VERSION
    assert payload["report_count"] == 2

    output = write_verification_reports_json(
        (report, report),
        tmp_path / "verification-reports.json",
    )
    written = json.loads(output.read_text(encoding="utf-8"))
    assert written["report_count"] == 2


def test_report_json_matches_versioned_golden_contract() -> None:
    golden_path = (
        Path(__file__).parents[2]
        / "fixtures"
        / "reporting"
        / "golden"
        / "verification_report_v1.json"
    )

    assert _report().to_dict() == json.loads(golden_path.read_text(encoding="utf-8"))
