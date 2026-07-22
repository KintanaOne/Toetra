from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from dsl.provenance.model import ArtifactProvenance, ReportProvenance
from dsl.reporting.evaluations import (
    ReportLoweringTrace,
    ReportModelEvaluation,
)
from dsl.reporting.model import (
    ReportAssignment,
    ReportNumericCompatibility,
    VerificationReport,
)
from dsl.reporting.values import json_safe_report_value

REPORT_SCHEMA = "forml.verification-report"
REPORT_COLLECTION_SCHEMA = "forml.verification-report-collection"
REPORT_SCHEMA_VERSION = 5  # Frozen for the FORML 1.x public contract.


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
            "backend_execution": _backend_execution_to_dict(report),
        },
        "summary": report.summary,
        "provenance": _provenance_to_dict(report.provenance),
        "numeric_compatibility": _numeric_compatibility_to_dict(
            report.numeric_compatibility
        ),
        **(
            {
                "model_evaluations": [
                    _model_evaluation_to_dict(item) for item in report.model_evaluations
                ]
            }
            if report.model_evaluations
            else {}
        ),
        "points": [
            {
                "name": point.name,
                "binding_kind": point.binding_kind,
                "provenance": json_safe_report_value(point.provenance),
                "inputs": [_assignment_to_dict(item) for item in point.inputs],
                "outputs": [_assignment_to_dict(item) for item in point.outputs],
            }
            for point in report.points
        ],
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

    report_items = tuple(reports)
    items = [verification_report_to_dict(report) for report in report_items]
    shared_provenance = _shared_provenance(report_items)
    return {
        "schema": REPORT_COLLECTION_SCHEMA,
        "schema_version": REPORT_SCHEMA_VERSION,
        "report_count": len(items),
        "provenance": _collection_provenance_to_dict(shared_provenance),
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


def _shared_provenance(
    reports: tuple[VerificationReport, ...],
) -> ReportProvenance | None:
    provenances = tuple(report.provenance for report in reports)
    if not provenances or any(item is None for item in provenances):
        return None
    first = provenances[0]
    assert first is not None
    if all(
        item is not None
        and item.input_fingerprint == first.input_fingerprint
        and item.captured_at_utc == first.captured_at_utc
        for item in provenances
    ):
        return first
    return None


def _collection_provenance_to_dict(
    provenance: ReportProvenance | None,
) -> dict[str, Any] | None:
    if provenance is None:
        return None
    compiler = provenance.compiler
    software = provenance.software
    return {
        "captured_at_utc": provenance.captured_at_utc,
        "completeness": provenance.completeness.value,
        "unavailable_inputs": list(provenance.unavailable_inputs),
        "fingerprints": {"inputs": provenance.input_fingerprint},
        "artifacts": {
            role: _artifact_provenance_to_dict(artifact)
            for role, artifact in provenance.artifacts.items()
        },
        "software": {
            "forml_version": software.forml_version,
            "forml_build_id": software.forml_build_id,
            "python_version": software.python_version,
            "python_implementation": software.python_implementation,
            "platform": software.platform,
            "components": dict(software.components),
        },
        "compiler_policy": {
            "preferred_normal_form": compiler.preferred_normal_form,
            "max_distribution_size": compiler.max_distribution_size,
            "allow_nnf_fallback": compiler.allow_nnf_fallback,
            "backend_hint": compiler.backend_hint,
            "strict": compiler.strict,
        },
    }


def _provenance_to_dict(
    provenance: ReportProvenance | None,
) -> dict[str, Any] | None:
    if provenance is None:
        return None
    compiler = provenance.compiler
    software = provenance.software
    return {
        "captured_at_utc": provenance.captured_at_utc,
        "completeness": provenance.completeness.value,
        "unavailable_inputs": list(provenance.unavailable_inputs),
        "fingerprints": {
            "inputs": provenance.input_fingerprint,
            "property": provenance.property_fingerprint,
            "route": provenance.route_fingerprint,
            "execution_policy": provenance.execution_policy_fingerprint,
            "verification": provenance.verification_fingerprint,
        },
        "artifacts": {
            role: _artifact_provenance_to_dict(artifact)
            for role, artifact in provenance.artifacts.items()
        },
        "software": {
            "forml_version": software.forml_version,
            "forml_build_id": software.forml_build_id,
            "python_version": software.python_version,
            "python_implementation": software.python_implementation,
            "platform": software.platform,
            "components": dict(software.components),
        },
        "compiler": {
            "preferred_normal_form": compiler.preferred_normal_form,
            "actual_normal_form": compiler.actual_normal_form,
            "max_distribution_size": compiler.max_distribution_size,
            "allow_nnf_fallback": compiler.allow_nnf_fallback,
            "backend_hint": compiler.backend_hint,
            "strict": compiler.strict,
            "source_ir": compiler.source_ir,
            "builder": compiler.builder,
        },
    }


def _artifact_provenance_to_dict(
    artifact: ArtifactProvenance,
) -> dict[str, Any]:
    fingerprint = artifact.fingerprint
    return {
        "role": artifact.role,
        "source_kind": artifact.source_kind,
        "status": artifact.status.value,
        "name": artifact.name,
        "fingerprint": (
            {
                "algorithm": fingerprint.algorithm,
                "digest": fingerprint.digest,
                "identifier": fingerprint.identifier,
                "size_bytes": fingerprint.size_bytes,
                "canonicalization": fingerprint.canonicalization,
            }
            if fingerprint is not None
            else None
        ),
        "unavailable_reason": artifact.unavailable_reason,
    }


def _backend_execution_to_dict(report: VerificationReport) -> dict[str, Any] | None:
    execution = report.backend_execution
    if execution is None:
        return None
    return {
        "status": execution.status,
        "duration_ms": execution.duration_ms,
        "reason": execution.reason,
        "backend_reason": execution.backend_reason,
        "policy": {
            "timeout_ms": execution.timeout_ms,
            "max_backend_units": execution.max_backend_units,
            "max_memory_mb": execution.max_memory_mb,
            "deterministic_seed": execution.deterministic_seed,
            "backend_options": dict(execution.backend_options),
        },
    }


def _numeric_compatibility_to_dict(
    compatibility: ReportNumericCompatibility | None,
) -> dict[str, Any] | None:
    if compatibility is None:
        return None

    return {
        "rule_id": compatibility.matched_rule_id,
        "support_status": compatibility.support_status,
        "classification": compatibility.classification,
        "semantic_target": compatibility.semantic_target,
        "conclusion_scope": compatibility.conclusion_scope,
        "evidence_id": compatibility.evidence_id,
        "source": {
            "framework_adapter_id": compatibility.framework_adapter_id,
            "framework_version": compatibility.framework_version,
            "model_family": compatibility.model_family,
            "execution_profile_id": compatibility.source_execution_profile_id,
        },
        "model_encoder": {
            "id": compatibility.model_encoder_id,
            "version": compatibility.model_encoder_version,
        },
        "backend": {
            "kind": compatibility.backend_kind,
            "adapter_id": compatibility.backend_adapter_id,
            "adapter_version": compatibility.backend_version,
            "profile_id": compatibility.backend_profile_id,
        },
        "property_numeric_requirements": list(
            compatibility.property_numeric_requirements
        ),
        "permitted_conclusions": list(compatibility.permitted_conclusions),
        "replay_required_for": list(compatibility.replay_required_for),
        "assumptions_and_preconditions": list(
            compatibility.assumptions_and_preconditions
        ),
        "diagnostics": list(compatibility.compatibility_diagnostics),
        "documentation_reference": compatibility.documentation_reference,
    }


def _model_evaluation_to_dict(
    evaluation: ReportModelEvaluation,
) -> dict[str, Any]:
    return {
        "model_identity": evaluation.model_identity,
        "point": evaluation.point_name,
        "binding_kind": evaluation.binding_kind,
        "output_name": evaluation.output_name,
        "decision_policy": {
            "native_probability_threshold": evaluation.native_probability_threshold,
            "native_decision_threshold": evaluation.native_decision_threshold,
            "equality_label": json_safe_report_value(evaluation.equality_label),
        },
        "predicted_label": json_safe_report_value(evaluation.predicted_label),
        "probabilities": [
            {
                "label": json_safe_report_value(item.label),
                "value": json_safe_report_value(item.value),
                "source": item.source,
                "precision_digits": item.precision_digits,
            }
            for item in evaluation.probabilities
        ],
        "quantities": [
            {
                "kind": item.kind,
                "semantic_profile_id": item.semantic_profile_id,
                "value": json_safe_report_value(item.value),
            }
            for item in evaluation.quantities
        ],
        "lowerings": [_lowering_trace_to_dict(item) for item in evaluation.lowerings],
    }


def _lowering_trace_to_dict(trace: ReportLoweringTrace) -> dict[str, Any]:
    source_intent = {
        "observable": trace.observable,
        "operator": trace.operator,
        "label": json_safe_report_value(trace.label),
        "property_threshold": trace.property_threshold,
        "property_value": json_safe_report_value(trace.property_value),
        "property_satisfied": trace.property_satisfied,
        "property_margin": json_safe_report_value(trace.property_margin),
        "logical_polarity": trace.logical_polarity,
    }
    if trace.related_point_name is not None:
        source_intent["related_point"] = trace.related_point_name
        source_intent["related_property_value"] = json_safe_report_value(
            trace.related_property_value
        )
    canonical_constraint = {
        "quantity_kind": trace.quantity_kind,
        "quantity_value": json_safe_report_value(trace.quantity_value),
        "operator": trace.canonical_operator,
        "threshold": trace.canonical_threshold,
        "margin": json_safe_report_value(trace.canonical_margin),
        "exact_threshold_expression": trace.exact_threshold_expression,
        "threshold_lower_bound": trace.threshold_lower_bound,
        "threshold_upper_bound": trace.threshold_upper_bound,
        "selected_bound": trace.selected_bound,
        "precision_digits": trace.precision_digits,
        "working_precision_digits": trace.working_precision_digits,
        "guard_digits": trace.guard_digits,
    }
    if trace.related_point_name is not None:
        canonical_constraint["related_quantity_value"] = json_safe_report_value(
            trace.related_quantity_value
        )
    if trace.canonical_formula_kind is not None:
        canonical_constraint["formula_kind"] = trace.canonical_formula_kind
    return {
        "source_intent": source_intent,
        "semantic_profile": {
            "id": trace.semantic_profile_id,
            "version": trace.semantic_profile_version,
        },
        "transformation": {
            "id": trace.transformation_id,
            "version": trace.transformation_version,
        },
        "canonical_constraint": canonical_constraint,
        "compatibility": {
            "classification": trace.compatibility_classification,
            "permitted_conclusions": list(trace.permitted_conclusions),
        },
    }


def _assignment_to_dict(assignment: ReportAssignment) -> dict[str, Any]:
    payload = {
        "name": assignment.display_name,
        "raw_name": assignment.raw_name,
        "kind": assignment.kind.value,
        "value": json_safe_report_value(assignment.value),
    }
    optional = {
        "point": assignment.point_name,
        "binding_kind": assignment.binding_kind,
        "model_identity": assignment.model_identity,
        "target": assignment.target_name,
        "output_name": assignment.output_name,
        "quantity_kind": assignment.quantity_kind,
        "semantic_profile_id": assignment.semantic_profile_id,
    }
    payload.update({key: value for key, value in optional.items() if value is not None})
    return payload


def _write_json(path: str | Path, content: str) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content + "\n", encoding="utf-8")
    return output
