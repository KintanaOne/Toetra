"""Strict reconstruction of replay evidence from Toetra JSON v6 reports."""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping

from toetra._backends.results import VerificationStatus
from toetra._reporting.evaluations import (
    ReportClassProbability,
    ReportModelEvaluation,
    ReportModelQuantity,
)
from toetra._reporting.json import (
    REPORT_COLLECTION_SCHEMA,
    REPORT_SCHEMA,
    REPORT_SCHEMA_VERSION,
)
from toetra._reporting.model import (
    ReportAssignment,
    ReportAssignmentKind,
    ReportPointEvidence,
)
from toetra._runtime.errors import VerificationConfigurationError
from toetra._runtime.execution_context import ExecutionContext


@dataclass(frozen=True)
class ArchivedReplayReport:
    """Minimal archived report representation required by replay semantics."""

    property_index: int
    status: VerificationStatus
    points: tuple[ReportPointEvidence, ...]
    model_evaluations: tuple[ReportModelEvaluation, ...]
    property_fingerprint: str
    input_fingerprint: str


@dataclass(frozen=True)
class ArchivedVerificationCollection:
    """Validated JSON v6 collection and its replay-relevant evidence."""

    path: Path
    input_fingerprint: str
    execution_context: ExecutionContext | None
    reports: tuple[ArchivedReplayReport, ...]

    @property
    def effective_target(self) -> str | None:
        if self.execution_context is None:
            return None
        return self.execution_context.effective_target


def load_archived_verification_collection(
    report: str | Path,
) -> ArchivedVerificationCollection:
    """Load one complete JSON v6 collection before any model reconstruction."""

    path = Path(report).expanduser().resolve()
    payload = _load_collection(path)
    input_fingerprint = _require_input_fingerprint(payload, path)
    execution_context = _optional_execution_context(payload)
    reports = _parse_reports(
        payload,
        execution_context=execution_context,
    )
    return ArchivedVerificationCollection(
        path=path,
        input_fingerprint=input_fingerprint,
        execution_context=execution_context,
        reports=reports,
    )


def _load_collection(path: Path) -> Mapping[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise VerificationConfigurationError(
            f"Archived verification report not found: {path}",
            code="REPLAY_REPORT_NOT_FOUND",
            stage="configuration",
            hint="Provide an existing JSON v6 verification report collection.",
            path=str(path),
        ) from error
    except (OSError, UnicodeError) as error:
        raise VerificationConfigurationError(
            f"Unable to read archived verification report: {path}",
            code="REPLAY_REPORT_UNREADABLE",
            stage="configuration",
            hint="Check file permissions and UTF-8 encoding.",
            path=str(path),
        ) from error
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as error:
        raise VerificationConfigurationError(
            "Archived verification report is not valid JSON.",
            code="REPLAY_REPORT_JSON_INVALID",
            stage="configuration",
            hint="Provide an unmodified Toetra JSON v6 report collection.",
            path=str(path),
            line=error.lineno,
            column=error.colno,
        ) from error
    if not isinstance(payload, dict):
        raise _invalid_report(path, "Report collection must be a JSON object.")
    if payload.get("schema") != REPORT_COLLECTION_SCHEMA:
        raise _invalid_report(path, "Unsupported report collection schema identity.")
    if payload.get("schema_version") != REPORT_SCHEMA_VERSION:
        raise _invalid_report(
            path,
            "Replay accepts only verification schema version 6.",
        )
    reports = payload.get("reports")
    count = payload.get("report_count")
    if (
        isinstance(count, bool)
        or not isinstance(count, int)
        or not isinstance(reports, list)
        or count != len(reports)
    ):
        raise _invalid_report(
            path,
            "Report collection count does not match its reports.",
        )
    return payload


def _require_input_fingerprint(payload: Mapping[str, Any], path: Path) -> str:
    provenance = _mapping(payload.get("provenance"), "collection.provenance")
    if provenance.get("completeness") != "complete":
        raise VerificationConfigurationError(
            "Archived report provenance is incomplete.",
            code="REPLAY_ARCHIVED_PROVENANCE_INCOMPLETE",
            stage="configuration",
            hint=(
                "Replay requires a report created from fully fingerprinted "
                "file inputs."
            ),
            path=str(path),
        )
    fingerprints = _mapping(provenance.get("fingerprints"), "collection.fingerprints")
    return _fingerprint(fingerprints.get("inputs"), "inputs")


def _optional_execution_context(
    payload: Mapping[str, Any],
) -> ExecutionContext | None:
    provenance = _mapping(payload.get("provenance"), "collection.provenance")
    return _execution_context_from_value(
        provenance.get("execution_context"),
        prefix="collection.execution_context",
    )


def _execution_context_from_value(
    raw_context: object,
    *,
    prefix: str,
) -> ExecutionContext | None:
    if raw_context is None:
        return None
    context = _mapping(raw_context, prefix)
    declared = _mapping(context.get("declared"), f"{prefix}.declared")
    effective = _mapping(context.get("effective"), f"{prefix}.effective")
    overrides = _mapping(context.get("overrides"), f"{prefix}.overrides")
    parsed = ExecutionContext(
        declared_model_reference=_required_text(
            declared.get("model"),
            f"{prefix}.declared.model",
        ),
        declared_target=_required_text(
            declared.get("target"),
            f"{prefix}.declared.target",
        ),
        declared_dataset_reference=_optional_text(
            declared.get("dataset"),
            f"{prefix}.declared.dataset",
        ),
        effective_model_reference=_required_text(
            effective.get("model"),
            f"{prefix}.effective.model",
        ),
        effective_target=_required_text(
            effective.get("target"),
            f"{prefix}.effective.target",
        ),
        effective_dataset_reference=_optional_text(
            effective.get("dataset"),
            f"{prefix}.effective.dataset",
        ),
        model_overridden=_required_bool(
            overrides.get("model"),
            f"{prefix}.overrides.model",
        ),
        target_overridden=_required_bool(
            overrides.get("target"),
            f"{prefix}.overrides.target",
        ),
        dataset_overridden=_required_bool(
            overrides.get("dataset"),
            f"{prefix}.overrides.dataset",
        ),
    )
    _validate_execution_context_flags(parsed, prefix=prefix)
    return parsed


def _validate_execution_context_flags(
    context: ExecutionContext,
    *,
    prefix: str,
) -> None:
    pairs = (
        (
            "model",
            context.model_overridden,
            context.declared_model_reference,
            context.effective_model_reference,
        ),
        (
            "target",
            context.target_overridden,
            context.declared_target,
            context.effective_target,
        ),
        (
            "dataset",
            context.dataset_overridden,
            context.declared_dataset_reference,
            context.effective_dataset_reference,
        ),
    )
    for name, overridden, declared, effective in pairs:
        if not overridden and declared != effective:
            raise _report_contract_error(
                f"{prefix}.{name} differs without an override flag."
            )
    if context.dataset_overridden and context.effective_dataset_reference is None:
        raise _report_contract_error(
            f"{prefix}.effective.dataset is required for a dataset override."
        )


def _parse_reports(
    payload: Mapping[str, Any],
    *,
    execution_context: ExecutionContext | None,
) -> tuple[ArchivedReplayReport, ...]:
    raw_reports = payload["reports"]
    assert isinstance(raw_reports, list)
    parsed = tuple(
        _parse_report(
            item,
            execution_context=execution_context,
        )
        for item in raw_reports
    )
    indices = [item.property_index for item in parsed]
    if len(indices) != len(set(indices)):
        raise VerificationConfigurationError(
            "Archived verification report contains duplicate property indices.",
            code="REPLAY_REPORT_DUPLICATE_PROPERTY",
            stage="configuration",
            hint="Provide an unmodified Toetra JSON v6 report collection.",
        )
    return parsed


def _parse_report(
    raw: object,
    *,
    execution_context: ExecutionContext | None,
) -> ArchivedReplayReport:
    report = _mapping(raw, "report")
    if report.get("schema") != REPORT_SCHEMA:
        raise _report_contract_error("Report item has an unsupported schema identity.")
    if report.get("schema_version") != REPORT_SCHEMA_VERSION:
        raise _report_contract_error("Report item must use schema version 6.")
    property_payload = _mapping(report.get("property"), "property")
    property_index = _non_negative_int(property_payload.get("index"), "property.index")
    execution = _mapping(report.get("execution"), "execution")
    status = _verification_status(execution.get("status"))
    provenance = _mapping(report.get("provenance"), "provenance")
    report_context = _execution_context_from_value(
        provenance.get("execution_context"),
        prefix="report.execution_context",
    )
    if report_context != execution_context:
        raise _report_contract_error(
            "Report execution context does not match collection provenance."
        )
    fingerprints = _mapping(provenance.get("fingerprints"), "provenance.fingerprints")
    input_fingerprint = _fingerprint(fingerprints.get("inputs"), "inputs")
    archived_property_fingerprint = _fingerprint(
        fingerprints.get("property"),
        "property",
    )
    points = tuple(
        _parse_point(item) for item in _sequence(report.get("points"), "points")
    )
    evaluations = tuple(
        _parse_model_evaluation(item)
        for item in _sequence(report.get("model_evaluations", []), "model_evaluations")
    )
    return ArchivedReplayReport(
        property_index=property_index,
        status=status,
        points=points,
        model_evaluations=evaluations,
        property_fingerprint=archived_property_fingerprint,
        input_fingerprint=input_fingerprint,
    )


def _parse_point(raw: object) -> ReportPointEvidence:
    point = _mapping(raw, "point")
    name = _required_text(point.get("name"), "point.name")
    binding_kind = _required_text(point.get("binding_kind"), "point.binding_kind")
    inputs = tuple(
        _parse_assignment(item, expected_kind=ReportAssignmentKind.INPUT)
        for item in _sequence(point.get("inputs"), "point.inputs")
    )
    outputs = tuple(
        _parse_assignment(item, expected_kind=ReportAssignmentKind.OUTPUT)
        for item in _sequence(point.get("outputs"), "point.outputs")
    )
    provenance = point.get("provenance")
    if provenance is not None and not isinstance(provenance, dict):
        raise _report_contract_error("point.provenance must be an object or null.")
    return ReportPointEvidence(
        name=name,
        binding_kind=binding_kind,
        inputs=inputs,
        outputs=outputs,
        provenance=provenance,
    )


def _parse_assignment(
    raw: object,
    *,
    expected_kind: ReportAssignmentKind,
) -> ReportAssignment:
    assignment = _mapping(raw, "assignment")
    kind = _required_text(assignment.get("kind"), "assignment.kind")
    if kind != expected_kind.value:
        raise _report_contract_error(
            f"Expected {expected_kind.value!r} assignment, got {kind!r}."
        )
    return ReportAssignment(
        raw_name=_required_text(assignment.get("raw_name"), "assignment.raw_name"),
        display_name=_required_text(assignment.get("name"), "assignment.name"),
        value=_decode_value(assignment.get("value")),
        kind=expected_kind,
        point_name=_optional_text(assignment.get("point"), "assignment.point"),
        binding_kind=_optional_text(
            assignment.get("binding_kind"),
            "assignment.binding_kind",
        ),
        model_identity=_optional_text(
            assignment.get("model_identity"),
            "assignment.model_identity",
        ),
        target_name=_optional_text(assignment.get("target"), "assignment.target"),
        output_name=_optional_text(
            assignment.get("output_name"),
            "assignment.output_name",
        ),
        quantity_kind=_optional_text(
            assignment.get("quantity_kind"),
            "assignment.quantity_kind",
        ),
        semantic_profile_id=_optional_text(
            assignment.get("semantic_profile_id"),
            "assignment.semantic_profile_id",
        ),
    )


def _parse_model_evaluation(raw: object) -> ReportModelEvaluation:
    evaluation = _mapping(raw, "model_evaluation")
    policy = _mapping(evaluation.get("decision_policy"), "decision_policy")
    probabilities = tuple(
        _parse_probability(item)
        for item in _sequence(evaluation.get("probabilities"), "probabilities")
    )
    quantities = tuple(
        _parse_quantity(item)
        for item in _sequence(evaluation.get("quantities"), "quantities")
    )
    return ReportModelEvaluation(
        model_identity=_required_text(
            evaluation.get("model_identity"),
            "model_evaluation.model_identity",
        ),
        point_name=_required_text(
            evaluation.get("point"),
            "model_evaluation.point",
        ),
        binding_kind=_required_text(
            evaluation.get("binding_kind"),
            "model_evaluation.binding_kind",
        ),
        output_name=_required_text(
            evaluation.get("output_name"),
            "model_evaluation.output_name",
        ),
        predicted_label=_decode_value(evaluation.get("predicted_label")),
        probabilities=probabilities,
        quantities=quantities,
        native_probability_threshold=_optional_text(
            policy.get("native_probability_threshold"),
            "decision_policy.native_probability_threshold",
        ),
        native_decision_threshold=_optional_text(
            policy.get("native_decision_threshold"),
            "decision_policy.native_decision_threshold",
        ),
        equality_label=_decode_value(policy.get("equality_label")),
        lowerings=(),
    )


def _parse_probability(raw: object) -> ReportClassProbability:
    probability = _mapping(raw, "probability")
    value = probability.get("value")
    decimal_value = None
    if value is not None:
        try:
            decimal_value = Decimal(str(value))
        except (InvalidOperation, ValueError) as error:
            raise _report_contract_error("Probability value is not numeric.") from error
    precision = probability.get("precision_digits", 50)
    if isinstance(precision, bool) or not isinstance(precision, int) or precision <= 0:
        raise _report_contract_error("Probability precision must be positive.")
    return ReportClassProbability(
        label=_decode_value(probability.get("label")),
        value=decimal_value,
        source=_required_text(probability.get("source"), "probability.source"),
        precision_digits=precision,
    )


def _parse_quantity(raw: object) -> ReportModelQuantity:
    quantity = _mapping(raw, "quantity")
    return ReportModelQuantity(
        kind=_required_text(quantity.get("kind"), "quantity.kind"),
        semantic_profile_id=_required_text(
            quantity.get("semantic_profile_id"),
            "quantity.semantic_profile_id",
        ),
        value=_decode_value(quantity.get("value")),
    )


def _decode_value(value: Any) -> Any:
    if isinstance(value, dict):
        if value.get("kind") == "rational":
            numerator = value.get("numerator")
            denominator = value.get("denominator")
            if (
                isinstance(numerator, bool)
                or not isinstance(numerator, int)
                or isinstance(denominator, bool)
                or not isinstance(denominator, int)
                or denominator == 0
            ):
                raise _report_contract_error("Invalid rational report value.")
            return Fraction(numerator, denominator)
        return {str(key): _decode_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_decode_value(item) for item in value]
    return value


def _verification_status(value: object) -> VerificationStatus:
    if not isinstance(value, str):
        raise _report_contract_error("execution.status must be text.")
    try:
        return VerificationStatus(value)
    except ValueError as error:
        raise _report_contract_error(
            f"Unsupported verification status: {value!r}."
        ) from error


def _mapping(value: object, name: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise _report_contract_error(f"{name} must be a JSON object.")
    return value


def _sequence(value: object, name: str) -> list[object]:
    if not isinstance(value, list):
        raise _report_contract_error(f"{name} must be a JSON array.")
    return value


def _required_text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise _report_contract_error(f"{name} must be non-empty text.")
    return value


def _optional_text(value: object, name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise _report_contract_error(f"{name} must be text or null.")
    return value


def _required_bool(value: object, name: str) -> bool:
    if not isinstance(value, bool):
        raise _report_contract_error(f"{name} must be a boolean.")
    return value


def _non_negative_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise _report_contract_error(f"{name} must be a non-negative integer.")
    return value


def _fingerprint(value: object, name: str) -> str:
    if (
        not isinstance(value, str)
        or not value.startswith("sha256:")
        or len(value) != 71
        or any(character not in "0123456789abcdef" for character in value[7:])
    ):
        raise _report_contract_error(f"Invalid {name} fingerprint.")
    return value


def _invalid_report(path: Path, message: str) -> VerificationConfigurationError:
    return VerificationConfigurationError(
        message,
        code="REPLAY_REPORT_CONTRACT_INVALID",
        stage="configuration",
        hint="Provide an unmodified Toetra JSON v6 report collection.",
        path=str(path),
    )


def _report_contract_error(message: str) -> VerificationConfigurationError:
    return VerificationConfigurationError(
        message,
        code="REPLAY_REPORT_CONTRACT_INVALID",
        stage="configuration",
        hint="Provide an unmodified Toetra JSON v6 report collection.",
    )
