from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import asdict, is_dataclass
from decimal import Decimal
from enum import Enum
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, cast

from dsl.reporting.model import ReportAssignment, VerificationReport

REPORT_SCHEMA = "forml.verification-report"
REPORT_COLLECTION_SCHEMA = "forml.verification-report-collection"
REPORT_SCHEMA_VERSION = 1


def verification_report_to_dict(report: VerificationReport) -> dict[str, Any]:
    """Serialize one report to the stable JSON-ready FORML contract."""

    return {
        "schema": REPORT_SCHEMA,
        "schema_version": REPORT_SCHEMA_VERSION,
        "property": {
            "index": report.property_index,
            "type": report.property_type.value,
            "semantics": report.semantics.value,
            "specification": report.specification,
        },
        "scope": {
            "kind": report.scope.kind,
            "quantifier": report.scope.quantifier,
            "variables": [
                {"name": variable.name, "role": variable.role}
                for variable in report.scope.variables
            ],
        },
        "execution": {
            "backend": report.backend.value,
            "backend_status": report.backend_status,
            "status": report.status.value,
            "assumption_count": report.assumption_count,
            "route_reason": report.route_reason,
        },
        "summary": report.summary,
        "assignments": {
            "inputs": [_assignment_to_dict(item) for item in report.inputs],
            "outputs": [_assignment_to_dict(item) for item in report.outputs],
            "auxiliary": [
                _assignment_to_dict(item) for item in report.auxiliary_assignments
            ],
        },
        "diagnostics": [
            {
                "code": diagnostic.code,
                "severity": diagnostic.severity.value,
                "message": diagnostic.message,
            }
            for diagnostic in report.diagnostics
        ],
    }


def verification_reports_to_dict(
    reports: Iterable[VerificationReport],
) -> dict[str, Any]:
    """Serialize several reports to a versioned collection contract."""

    items = [verification_report_to_dict(report) for report in reports]
    return {
        "schema": REPORT_COLLECTION_SCHEMA,
        "schema_version": REPORT_SCHEMA_VERSION,
        "report_count": len(items),
        "reports": items,
    }


def verification_report_to_json(
    report: VerificationReport,
    *,
    indent: int | None = 2,
) -> str:
    """Return one report as deterministic UTF-8 JSON text."""

    return json.dumps(
        verification_report_to_dict(report),
        ensure_ascii=False,
        indent=indent,
    )


def verification_reports_to_json(
    reports: Iterable[VerificationReport],
    *,
    indent: int | None = 2,
) -> str:
    """Return a collection of reports as deterministic UTF-8 JSON text."""

    return json.dumps(
        verification_reports_to_dict(reports),
        ensure_ascii=False,
        indent=indent,
    )


def write_verification_report_json(
    report: VerificationReport,
    path: str | Path,
    *,
    indent: int | None = 2,
) -> Path:
    """Write one versioned report and return the resolved output path."""

    return _write_json(path, verification_report_to_json(report, indent=indent))


def write_verification_reports_json(
    reports: Iterable[VerificationReport],
    path: str | Path,
    *,
    indent: int | None = 2,
) -> Path:
    """Write a versioned report collection and return the output path."""

    return _write_json(path, verification_reports_to_json(reports, indent=indent))


def _assignment_to_dict(assignment: ReportAssignment) -> dict[str, Any]:
    return {
        "name": assignment.display_name,
        "raw_name": assignment.raw_name,
        "kind": assignment.kind.value,
        "value": _json_safe_value(assignment.value),
    }


def _json_safe_value(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value

    if isinstance(value, Enum):
        return _json_safe_value(value.value)

    if isinstance(value, Decimal):
        return str(value)

    if isinstance(value, Fraction):
        return _rational_value(value.numerator, value.denominator)

    numerator = getattr(value, "numerator_as_long", None)
    denominator = getattr(value, "denominator_as_long", None)
    if callable(numerator) and callable(denominator):
        numerator_fn = cast(Callable[[], int], numerator)
        denominator_fn = cast(Callable[[], int], denominator)
        return _rational_value(numerator_fn(), denominator_fn())

    as_long = getattr(value, "as_long", None)
    if callable(as_long):
        try:
            return as_long()
        except (ArithmeticError, ValueError):
            pass

    if isinstance(value, Mapping):
        return {str(key): _json_safe_value(item) for key, item in value.items()}

    if isinstance(value, (list, tuple, set, frozenset)):
        return [_json_safe_value(item) for item in value]

    if is_dataclass(value) and not isinstance(value, type):
        return _json_safe_value(asdict(value))

    return str(value)


def _rational_value(numerator: int, denominator: int) -> int | dict[str, Any]:
    if denominator == 1:
        return numerator
    return {
        "kind": "rational",
        "numerator": numerator,
        "denominator": denominator,
        "text": f"{numerator}/{denominator}",
    }


def _write_json(path: str | Path, content: str) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content + "\n", encoding="utf-8")
    return output
