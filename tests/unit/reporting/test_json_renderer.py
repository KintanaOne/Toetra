from __future__ import annotations

import json
from fractions import Fraction

import z3

from toetra._backends.diagnostics import (
    BackendDiagnosticSeverity,
    BackendResultDiagnostic,
)
from toetra._backends.execution import (
    BackendExecutionPolicy,
    BackendExecutionStatus,
)
from toetra._backends.results import VerificationStatus
from toetra._compiler.ir.ir2.enums import VerificationSemantics
from toetra._language.vocabulary.backends import EnumBackend
from toetra._language.vocabulary.properties import EnumProperty
from toetra._provenance.model import (
    ArtifactProvenance,
    CompilerProvenance,
    ContentFingerprint,
    ExecutionContextProvenance,
    FingerprintStatus,
    ProvenanceCompleteness,
    ReportProvenance,
    SoftwareProvenance,
)
from toetra._reporting.json import (
    REPORT_COLLECTION_SCHEMA,
    REPORT_SCHEMA,
    REPORT_SCHEMA_VERSION,
    verification_reports_to_dict,
    write_verification_reports_json,
)
from toetra._reporting.model import (
    ReportAssignment,
    ReportAssignmentKind,
    ReportBackendExecution,
    ReportScope,
    ReportScopeVariable,
    VerificationReport,
)
from tests.support.paths import GOLDEN_ROOT


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
        backend_execution=ReportBackendExecution(
            status=BackendExecutionStatus.SAT.value,
            duration_ms=12.5,
            reason=None,
            backend_reason=None,
            timeout_ms=BackendExecutionPolicy().timeout_ms,
            max_backend_units=None,
            max_memory_mb=None,
            deterministic_seed=None,
            backend_options={},
        ),
        provenance=ReportProvenance(
            captured_at_utc="2026-07-19T12:00:00Z",
            input_fingerprint="sha256:" + "1" * 64,
            completeness=ProvenanceCompleteness.COMPLETE,
            unavailable_inputs=(),
            property_fingerprint="sha256:" + "2" * 64,
            route_fingerprint="sha256:" + "3" * 64,
            execution_policy_fingerprint="sha256:" + "4" * 64,
            verification_fingerprint="sha256:" + "5" * 64,
            artifacts={
                "specification": ArtifactProvenance(
                    role="specification",
                    source_kind="inline_text",
                    status=FingerprintStatus.AVAILABLE,
                    fingerprint=ContentFingerprint(
                        algorithm="sha256",
                        digest="a" * 64,
                        size_bytes=28,
                        canonicalization="utf8_compiler_source",
                    ),
                ),
                "model": ArtifactProvenance(
                    role="model",
                    source_kind="schema_only",
                    status=FingerprintStatus.NOT_PROVIDED,
                ),
            },
            execution_context=ExecutionContextProvenance(
                declared_model_reference="model.joblib",
                declared_target="score",
                declared_dataset_reference=None,
                effective_model_reference="candidate.joblib",
                effective_target="risk_score",
                effective_dataset_reference="reference.csv",
                model_overridden=True,
                target_overridden=True,
                dataset_overridden=True,
            ),
            software=SoftwareProvenance(
                toetra_version="1.0.0rc1",
                toetra_build_id="git:abc123",
                python_version="3.11.9",
                python_implementation="CPython",
                platform="Linux-6.0-x86_64",
                components={"z3-solver": "4.16.0.0"},
            ),
            compiler=CompilerProvenance(
                preferred_normal_form="nnf",
                actual_normal_form="nnf",
                max_distribution_size=256,
                allow_nnf_fallback=True,
                backend_hint="Z3",
                strict=True,
                source_ir="IR2",
                builder="IR2Builder",
            ),
        ),
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
    assert payload["provenance"]["fingerprints"]["verification"] == (
        "sha256:" + "5" * 64
    )
    assert payload["provenance"]["artifacts"]["model"]["status"] == ("not_provided")
    assert payload["provenance"]["execution_context"] == {
        "declared": {
            "model": "model.joblib",
            "target": "score",
            "dataset": None,
        },
        "effective": {
            "model": "candidate.joblib",
            "target": "risk_score",
            "dataset": "reference.csv",
        },
        "overrides": {
            "model": True,
            "target": True,
            "dataset": True,
        },
    }
    software = payload["provenance"]["software"]
    assert software["toetra_version"] == "1.0.0rc1"
    assert software["toetra_build_id"] == "git:abc123"
    assert "forml_version" not in software
    assert "forml_build_id" not in software


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
    golden_path = GOLDEN_ROOT / "reporting" / "verification_report_v6.json"

    assert _report().to_dict() == json.loads(golden_path.read_text(encoding="utf-8"))
