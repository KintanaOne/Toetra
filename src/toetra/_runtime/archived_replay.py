"""Replay archived JSON v6 verification evidence without invoking a solver."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from html import escape
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, Sequence

from toetra._backends.results import VerificationStatus
from toetra._compiler.ir.ir2.dsl.nodes import VerificationTaskIR2
from toetra._provenance.builder import property_fingerprint
from toetra._reporting.json import REPORT_COLLECTION_SCHEMA, REPORT_SCHEMA_VERSION
from toetra._reporting.values import json_safe_report_value
from toetra._runtime.archived_report import (
    ArchivedReplayReport,
    load_archived_verification_collection,
)
from toetra._runtime import api as runtime_api
from toetra._runtime.errors import (
    ReplayUnavailableError,
    VerificationConfigurationError,
)
from toetra._runtime.execution_context import (
    ExecutionContext,
    resolve_execution_context,
)
from toetra._runtime.preflight import ExecutablePlan, build_executable_plan
from toetra._runtime.replay import CounterexampleReplay, PointReplay
from toetra._runtime.replay_engine import replay_verification_report

REPLAY_COLLECTION_SCHEMA = "toetra.replay-report-collection"
REPLAY_COLLECTION_SCHEMA_VERSION = 1
_REPLAYABLE_STATUSES = {
    VerificationStatus.COUNTEREXAMPLE,
    VerificationStatus.WITNESS,
}


@dataclass(frozen=True)
class ReplayItemResult:
    """One selected archived property and its concrete replay conclusion."""

    property_index: int
    formal_status: VerificationStatus
    availability: str
    conclusion: str
    tolerance: float
    replay: CounterexampleReplay | None = field(default=None, repr=False)
    reason: str | None = None

    @property
    def is_inconsistent(self) -> bool:
        return self.conclusion == "inconsistent"

    @property
    def is_inconclusive(self) -> bool:
        return self.conclusion in {"indeterminate", "unavailable"}

    def to_dict(self) -> dict[str, Any]:
        replay = self.replay
        return {
            "property_index": self.property_index,
            "formal_status": self.formal_status.value,
            "availability": self.availability,
            "conclusion": self.conclusion,
            "reason": self.reason,
            "tolerance": self.tolerance,
            "max_absolute_error": (
                replay.max_absolute_error if replay is not None else None
            ),
            "restriction_satisfied": (
                replay.relation_satisfied if replay is not None else None
            ),
            "assertion_satisfied": (
                replay.assertion_satisfied if replay is not None else None
            ),
            "expected_assertion_satisfied": (
                replay.expected_assertion_satisfied if replay is not None else None
            ),
            "points": (
                [_point_to_dict(name, point) for name, point in replay.points.items()]
                if replay is not None
                else []
            ),
        }


@dataclass(frozen=True)
class ReplayCollectionResult:
    """Completed replay result suitable for text, JSON, or HTML output."""

    report_path: Path
    input_fingerprint: str
    tolerance: float
    requested_properties: tuple[int, ...]
    results: tuple[ReplayItemResult, ...]
    consumed_paths: tuple[Path, ...] = field(repr=False)

    @property
    def exit_code(self) -> int:
        if any(item.is_inconsistent for item in self.results):
            return 1
        if not self.results or any(item.is_inconclusive for item in self.results):
            return 2
        return 0

    @property
    def conclusion(self) -> str:
        return {
            0: "consistent",
            1: "inconsistent",
            2: "inconclusive",
        }[self.exit_code]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": REPLAY_COLLECTION_SCHEMA,
            "schema_version": REPLAY_COLLECTION_SCHEMA_VERSION,
            "report": {
                "path": str(self.report_path),
                "schema": REPORT_COLLECTION_SCHEMA,
                "schema_version": REPORT_SCHEMA_VERSION,
                "input_fingerprint": self.input_fingerprint,
            },
            "tolerance": self.tolerance,
            "requested_properties": list(self.requested_properties),
            "selected_count": len(self.results),
            "available_count": sum(
                item.availability == "available" for item in self.results
            ),
            "conclusion": self.conclusion,
            "results": [item.to_dict() for item in self.results],
            "software": {"toetra_version": _distribution_version()},
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def to_text(self) -> str:
        lines = [
            "Toetra Archived Replay",
            f"report: {self.report_path}",
            f"selected properties: {len(self.results)}",
            f"tolerance: {self.tolerance:g}",
            f"conclusion: {self.conclusion.upper()}",
        ]
        for item in self.results:
            lines.append("")
            lines.append(
                f"Property {item.property_index} [{item.formal_status.value}] "
                f"{item.conclusion.upper()}"
            )
            if item.reason:
                lines.append(f"reason: {item.reason}")
            if item.replay is not None:
                lines.append(item.replay.to_text())
        if not self.results:
            lines.append("")
            lines.append("No replayable finding was selected.")
        return "\n".join(lines)

    def to_html(self) -> str:
        sections = []
        for item in self.results:
            details = (
                item.replay.to_html()
                if item.replay is not None
                else f"<p>{escape(item.reason or 'Replay unavailable.')}</p>"
            )
            sections.append(
                "<section>"
                f"<h2>Property {item.property_index}</h2>"
                f"<p>Formal status: {escape(item.formal_status.value)}</p>"
                f"<p>Conclusion: {escape(item.conclusion)}</p>"
                f"{details}"
                "</section>"
            )
        if not sections:
            sections.append("<p>No replayable finding was selected.</p>")
        return (
            '<!doctype html><html lang="en"><head><meta charset="utf-8">'
            "<title>Toetra Archived Replay</title></head><body>"
            "<h1>Toetra Archived Replay</h1>"
            f"<p>Report: {escape(str(self.report_path))}</p>"
            f"<p>Conclusion: {escape(self.conclusion)}</p>"
            f"{''.join(sections)}</body></html>"
        )


def replay_archived_report(
    report: str | Path,
    *,
    specification: str | Path,
    model: str | Path | None = None,
    dataset: str | Path | None = None,
    anchor_source: str | Path | None = None,
    target: str | None = None,
    property_indices: Sequence[int] = (),
    tolerance: float = 1e-9,
) -> ReplayCollectionResult:
    """Replay selected archived findings against the archived effective context."""

    if not math.isfinite(tolerance) or tolerance < 0:
        raise VerificationConfigurationError(
            "Replay tolerance must be a finite non-negative number.",
            code="REPLAY_TOLERANCE_INVALID",
            stage="configuration",
            hint="Use a finite value greater than or equal to zero.",
        )

    archive = load_archived_verification_collection(report)
    requested = _deduplicate_indices(property_indices)
    selected = _select_reports(archive.reports, requested=requested)
    replay_context = _replay_execution_context(
        archive.execution_context,
        specification=specification,
        target=target,
    )
    plan = build_executable_plan(
        specification,
        model=model,
        dataset=dataset,
        anchor_source=anchor_source,
        require_translation=False,
        execution_context=replay_context,
    )
    if plan.provenance.completeness.value != "complete":
        raise VerificationConfigurationError(
            "Current replay inputs do not provide complete provenance.",
            code="REPLAY_PROVENANCE_INCOMPLETE",
            stage="configuration",
            hint="Use file-backed specification, model, dataset, and anchors.",
        )
    if plan.provenance.input_fingerprint != archive.input_fingerprint:
        raise VerificationConfigurationError(
            "Replay inputs do not match the archived verification provenance.",
            code="REPLAY_INPUT_FINGERPRINT_MISMATCH",
            stage="configuration",
            hint="Use the exact specification, model, dataset, and anchor artifacts.",
            path=str(archive.path),
        )

    tasks = {item.index: item.task for item in plan.properties}
    results = tuple(
        _replay_one(
            archived,
            plan=plan,
            task=tasks.get(archived.property_index),
            tolerance=tolerance,
        )
        for archived in selected
    )
    return ReplayCollectionResult(
        report_path=archive.path,
        input_fingerprint=archive.input_fingerprint,
        tolerance=tolerance,
        requested_properties=requested,
        results=results,
        consumed_paths=_consumed_paths(archive.path, plan),
    )


def _replay_execution_context(
    archived: ExecutionContext | None,
    *,
    specification: str | Path,
    target: str | None,
) -> ExecutionContext:
    if archived is not None:
        if target is not None and target != archived.effective_target:
            raise VerificationConfigurationError(
                "Target override does not match the archived effective target.",
                code="REPLAY_EXECUTION_CONTEXT_MISMATCH",
                stage="configuration",
                hint=(
                    "Replay reconstructs the historical target. Run a new "
                    "verification to use another target."
                ),
            )
        return archived

    loaded = runtime_api._load_specification(specification)
    if target is not None and target != loaded.target:
        raise VerificationConfigurationError(
            "Legacy report cannot establish the requested target override.",
            code="REPLAY_EXECUTION_CONTEXT_MISMATCH",
            stage="configuration",
            hint="Use the target declared by the archived specification.",
        )
    return resolve_execution_context(
        declared_model_reference=loaded.model_reference,
        declared_target=loaded.target,
        declared_dataset_reference=loaded.dataset_reference,
        model=None,
        target=None,
        dataset=None,
    )


def _replay_one(
    report: ArchivedReplayReport,
    *,
    plan: ExecutablePlan,
    task: VerificationTaskIR2 | None,
    tolerance: float,
) -> ReplayItemResult:
    if task is None:
        raise VerificationConfigurationError(
            (
                f"Archived property index {report.property_index} "
                "is absent from the specification."
            ),
            code="REPLAY_PROPERTY_INDEX_MISMATCH",
            stage="configuration",
            hint="Use the exact specification used to create the report.",
        )
    current_property_fingerprint = property_fingerprint(
        task,
        property_index=report.property_index,
    )
    if current_property_fingerprint != report.property_fingerprint:
        raise VerificationConfigurationError(
            f"Property {report.property_index} does not match archived provenance.",
            code="REPLAY_PROPERTY_FINGERPRINT_MISMATCH",
            stage="configuration",
            hint="Use the exact specification and preserve property ordering.",
        )
    if report.input_fingerprint != plan.provenance.input_fingerprint:
        raise VerificationConfigurationError(
            f"Property {report.property_index} carries inconsistent input provenance.",
            code="REPLAY_REPORT_PROVENANCE_MISMATCH",
            stage="configuration",
            hint="Use an unmodified JSON v6 report collection.",
        )
    if report.status not in _REPLAYABLE_STATUSES:
        return ReplayItemResult(
            property_index=report.property_index,
            formal_status=report.status,
            availability="unavailable",
            conclusion="unavailable",
            tolerance=tolerance,
            reason=(
                f"Formal status {report.status.value!r} has no concrete "
                "evidence to replay."
            ),
        )
    if plan.model is None:
        raise VerificationConfigurationError(
            "Archived replay requires a concrete model artifact.",
            code="REPLAY_MODEL_REQUIRED",
            stage="configuration",
            hint="Provide the model file used for the archived verification.",
        )

    try:
        replay = replay_verification_report(
            report,
            task=task,
            schema=plan.schema,
            model=plan.model,
            tolerance=tolerance,
        )
    except ReplayUnavailableError as error:
        return ReplayItemResult(
            property_index=report.property_index,
            formal_status=report.status,
            availability="unavailable",
            conclusion="unavailable",
            tolerance=tolerance,
            reason=str(error),
        )

    conclusion = "consistent" if replay.is_consistent else "inconsistent"
    if replay.is_consistent and replay.assertion_satisfied is None:
        conclusion = "indeterminate"
    return ReplayItemResult(
        property_index=report.property_index,
        formal_status=report.status,
        availability="available",
        conclusion=conclusion,
        tolerance=tolerance,
        replay=replay,
    )


def _select_reports(
    reports: tuple[ArchivedReplayReport, ...],
    *,
    requested: tuple[int, ...],
) -> tuple[ArchivedReplayReport, ...]:
    by_index = {item.property_index: item for item in reports}
    if requested:
        missing = [index for index in requested if index not in by_index]
        if missing:
            rendered = ", ".join(str(index) for index in missing)
            raise VerificationConfigurationError(
                f"Archived report has no property index: {rendered}",
                code="REPLAY_PROPERTY_NOT_FOUND",
                stage="configuration",
                hint=(
                    "Select zero-based property indices present in the "
                    "report collection."
                ),
            )
        return tuple(by_index[index] for index in requested)
    return tuple(item for item in reports if item.status in _REPLAYABLE_STATUSES)


def _deduplicate_indices(values: Sequence[int]) -> tuple[int, ...]:
    ordered: list[int] = []
    seen: set[int] = set()
    for value in values:
        if value < 0:
            raise VerificationConfigurationError(
                "Replay property indices must be non-negative.",
                code="REPLAY_PROPERTY_INDEX_INVALID",
                stage="configuration",
                hint="Use zero-based property indices.",
            )
        if value not in seen:
            seen.add(value)
            ordered.append(value)
    return tuple(ordered)


def _consumed_paths(report_path: Path, plan: ExecutablePlan) -> tuple[Path, ...]:
    ordered = (report_path, *plan.consumed_paths)
    unique: list[Path] = []
    seen: set[Path] = set()
    for path in ordered:
        resolved = path.expanduser().resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(resolved)
    return tuple(unique)


def _point_to_dict(name: str, point: PointReplay) -> dict[str, Any]:
    return {
        "name": name,
        "inputs": json_safe_report_value(dict(point.inputs)),
        "formal_outputs": json_safe_report_value(dict(point.backend_outputs)),
        "model_outputs": json_safe_report_value(dict(point.model_outputs)),
        "absolute_errors": json_safe_report_value(dict(point.absolute_errors)),
        "evaluations": [
            {
                "output_name": item.output_name,
                "formal_label": json_safe_report_value(item.formal_label),
                "model_label": json_safe_report_value(item.model_label),
                "label_matches": item.label_matches,
                "formal_probabilities": json_safe_report_value(
                    dict(item.formal_probabilities)
                ),
                "model_probabilities": json_safe_report_value(
                    dict(item.model_probabilities)
                ),
                "probability_errors": json_safe_report_value(
                    dict(item.probability_errors)
                ),
                "formal_quantities": json_safe_report_value(
                    dict(item.formal_quantities)
                ),
                "model_quantities": json_safe_report_value(dict(item.model_quantities)),
                "quantity_errors": json_safe_report_value(dict(item.quantity_errors)),
            }
            for item in point.evaluations
        ],
    }


def _distribution_version() -> str:
    try:
        return version("toetra")
    except PackageNotFoundError:
        return "unknown"
