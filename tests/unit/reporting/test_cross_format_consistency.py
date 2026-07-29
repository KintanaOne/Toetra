from __future__ import annotations

from html import unescape
from typing import cast

from toetra._backends.diagnostics import (
    BackendDiagnosticSeverity,
    BackendResultDiagnostic,
)
from toetra._backends.results import VerificationResult, VerificationStatus
from toetra._backends.router import BackendRoute
from toetra._compiler.ir.ir2.dsl.nodes import VerificationTaskIR2
from toetra._compiler.ir.ir2.enums import VerificationSemantics
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._language.vocabulary.backends import EnumBackend
from toetra._language.vocabulary.properties import EnumProperty
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema
from toetra._reporting.model import (
    ReportAssignment,
    ReportAssignmentKind,
    ReportBackendExecution,
    ReportNumericCompatibility,
    ReportScope,
    ReportScopeVariable,
    VerificationReport,
)
from toetra._runtime.session import VerificationExecution, VerificationSession


def _report() -> VerificationReport:
    return VerificationReport(
        property_index=0,
        property_type=EnumProperty.LOGIC,
        semantics=VerificationSemantics.REFUTATION,
        scope=ReportScope(
            kind="quantifier",
            quantifier="forall",
            variables=(ReportScopeVariable(name="applicant", role="bound"),),
        ),
        specification="target[applicant] <= 7.0",
        backend=EnumBackend.Z3,
        backend_status="unknown",
        status=VerificationStatus.UNKNOWN,
        summary="Verification inconclusive: the backend execution timed out.",
        assignments=(
            ReportAssignment(
                raw_name="applicant.income",
                display_name="applicant.income",
                value=3,
                kind=ReportAssignmentKind.INPUT,
                point_name="applicant",
                binding_kind="bound",
            ),
        ),
        diagnostics=(
            BackendResultDiagnostic(
                code="EXECUTION_TIMEOUT",
                severity=BackendDiagnosticSeverity.WARNING,
                message="The total property deadline expired.",
            ),
        ),
        assumption_count=2,
        route_reason="requested backend satisfies the declared route",
        numeric_compatibility=ReportNumericCompatibility(
            matched_rule_id="sklearn-affine-to-z3-real",
            support_status="supported",
            classification="lossy",
            semantic_target="toetra.real_affine_extracted_model",
            conclusion_scope="semantic_target_only",
            evidence_id="ADR-0018#sklearn-affine",
            framework_adapter_id="toetra.sklearn",
            framework_version="1.8",
            model_family="affine_regression",
            source_execution_profile_id="sklearn.float64",
            model_encoder_id="toetra.affine-equation",
            model_encoder_version="1",
            backend_kind="smt",
            backend_adapter_id="toetra.z3",
            backend_profile_id="z3.real-arithmetic",
            backend_version="4.15",
            property_numeric_requirements=("affine_arithmetic",),
            permitted_conclusions=("universal_proof", "universal_counterexample"),
            replay_required_for=("universal_counterexample",),
            assumptions_and_preconditions=("All numeric contributors are finite.",),
            compatibility_diagnostics=(
                "The concrete floating execution is not bit-exact.",
            ),
            documentation_reference="docs/contracts/numeric-semantics.md",
        ),
        backend_execution=ReportBackendExecution(
            status="timeout",
            duration_ms=750.25,
            reason="The total property deadline expired.",
            backend_reason="timeout",
            timeout_ms=750,
            max_backend_units=100,
            max_memory_mb=32,
            deterministic_seed=4,
            backend_options={"smt.random_seed": 4},
        ),
    )


def _schema() -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features={
            "income": FeatureSchema(name="income", dtype=EnumDataType.FLOAT),
        },
        target="score",
        task="regression",
        target_dtype=EnumDataType.FLOAT,
        metadata={},
    )


def _session(report: VerificationReport) -> VerificationSession:
    execution = VerificationExecution(
        task=cast(VerificationTaskIR2, object()),
        route=cast(BackendRoute, object()),
        result=cast(VerificationResult, object()),
        report=report,
    )
    return VerificationSession(
        source=report.specification,
        specification_path=None,
        schema=_schema(),
        executions=(execution,),
    )


def test_human_renderers_share_the_same_conclusion_and_trust_context() -> None:
    report = _report()
    text = report.to_text()
    html = report.to_html()
    visible_html = unescape(html)

    shared_values = (
        "unknown",
        report.summary,
        report.specification,
        report.route_reason,
        "timeout",
        "750.250 ms",
        "100",
        "32 MB",
        "smt.random_seed=4",
        "sklearn-affine-to-z3-real",
        "toetra.real_affine_extracted_model",
        "semantic_target_only",
        "universal_counterexample",
        "EXECUTION_TIMEOUT",
    )
    for value in shared_values:
        assert value.lower() in text.lower()
        assert value.lower() in visible_html.lower()

    assert report._repr_html_() == html


def test_records_preserve_the_machine_evidence_from_json_v6() -> None:
    report = _report()
    session = _session(report)
    report_payload = report.to_dict()
    collection = session.to_dict()
    record = session.to_records()[0]

    assert report_payload["schema_version"] == 6
    assert collection["schema_version"] == 6
    assert collection["reports"][0] == report_payload
    assert record["status"] == report_payload["execution"]["status"]
    assert record["summary"] == report_payload["summary"]
    assert record["route_reason"] == report_payload["execution"]["route_reason"]
    assert (
        record["backend_execution"] == report_payload["execution"]["backend_execution"]
    )
    assert record["numeric_compatibility"] == report_payload["numeric_compatibility"]
    assert record["provenance"] == report_payload["provenance"]
    assert record["point_evidence"] == report_payload["points"]
    assert record["assignments"] == report_payload["assignments"]
    assert record["model_evaluations"] == []
    assert record["diagnostics"] == report_payload["diagnostics"]

    frame = session.to_dataframe()
    assert frame.loc[0, "backend_execution"] == record["backend_execution"]
    assert frame.loc[0, "numeric_compatibility"] == record["numeric_compatibility"]


def test_session_jupyter_representation_is_the_html_renderer() -> None:
    session = _session(_report())

    assert session._repr_html_() == session.to_html()
