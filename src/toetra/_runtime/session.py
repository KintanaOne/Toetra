from __future__ import annotations

import sys
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field, replace
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, TextIO, overload

from toetra._backends.results import VerificationResult, VerificationStatus
from toetra._backends.router import BackendRoute
from toetra._compiler.ir.ir2.dsl.nodes import VerificationTaskIR2
from toetra._provenance.model import VerificationProvenanceContext
from toetra._reporting.html import (
    HtmlRenderOptions,
    render_verification_reports_html,
    write_verification_reports_html,
)
from toetra._reporting.text import (
    TextRenderOptions,
    render_verification_reports_text,
)
from toetra._reporting.model import VerificationReport
from toetra._reporting.json import (
    verification_reports_to_dict,
    verification_reports_to_json,
    write_verification_reports_json,
)
from toetra._reporting.accessors import (
    report_output_values_by_point,
    report_point_values,
)
from toetra._runtime.replay import CounterexampleReplay
from toetra._runtime.replay_engine import replay_verification_report
from toetra._models.schema.model_schema import ModelSchema

if TYPE_CHECKING:
    from toetra._runtime.model_observer import ModelObserverRegistry
    from toetra._compiler.semantic.symbols.point import ResolvedAnchorBinding


_FAILURE_STATUSES = frozenset(
    {
        VerificationStatus.COUNTEREXAMPLE,
        VerificationStatus.NO_WITNESS,
    }
)
_SUCCESS_STATUSES = frozenset(
    {
        VerificationStatus.PROVED,
        VerificationStatus.WITNESS,
    }
)


def _unique_group_values(
    grouped: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any] | None:
    """Flatten a grouped value only when a single point makes it unambiguous."""

    if len(grouped) > 1:
        return None
    if grouped:
        return dict(next(iter(grouped.values())))
    return {}


def _stream_accepts_text(stream: TextIO, text: str) -> bool:
    """Return whether the stream's declared encoding can represent the text."""

    encoding = getattr(stream, "encoding", None)
    if not encoding:
        return True

    try:
        text.encode(encoding)
    except (LookupError, UnicodeEncodeError):
        return False
    return True


def _escape_text_for_stream(stream: TextIO, text: str) -> str:
    """Escape residual characters unsupported by a legacy text stream."""

    encoding = getattr(stream, "encoding", None)
    if not encoding:
        return text
    try:
        return text.encode(
            encoding,
            errors="backslashreplace",
        ).decode(encoding)
    except LookupError:
        return text


@dataclass(frozen=True)
class VerificationExecution:
    """One compiled, routed, executed and reported Toetra property."""

    task: VerificationTaskIR2
    route: BackendRoute
    result: VerificationResult
    report: VerificationReport


@dataclass(frozen=True)
class VerificationFinding:
    """Ergonomic user view over one completed verification property."""

    report: VerificationReport
    task: VerificationTaskIR2 = field(compare=False)
    schema: ModelSchema = field(compare=False)
    _model: object | None = field(default=None, repr=False, compare=False)

    @property
    def status(self) -> VerificationStatus:
        return self.report.status

    @property
    def input_values(self) -> dict[str, Any]:
        return self.report.input_values

    @property
    def qualified_input_values(self) -> dict[str, Any]:
        return self.report.qualified_input_values

    @property
    def output_values(self) -> dict[str, Any]:
        return self.report.output_values

    @property
    def point_values(self) -> dict[str, dict[str, Any]]:
        return report_point_values(self.report)

    @property
    def output_values_by_point(self) -> dict[str, dict[str, Any]]:
        return report_output_values_by_point(self.report)

    def replay(
        self,
        model: object | None = None,
        *,
        tolerance: float = 1e-9,
        observer_registry: ModelObserverRegistry | None = None,
    ) -> CounterexampleReplay:
        """Replay this assignment on the original or explicitly supplied model."""

        resolved_model = model if model is not None else self._model
        if resolved_model is None:
            from toetra._runtime.errors import ReplayUnavailableError

            raise ReplayUnavailableError(
                "No model instance is attached to this session. Pass model=... "
                "or call verify(...) with serialized model artifacts."
            )
        task = self.task
        if task is None:
            from toetra._runtime.errors import ReplayUnavailableError

            raise ReplayUnavailableError(
                "No compiled verification task is attached to this finding"
            )
        return replay_verification_report(
            self.report,
            task=task,
            schema=self.schema,
            model=resolved_model,
            tolerance=tolerance,
            observer_registry=observer_registry,
        )

    def to_text(self) -> str:
        return self.report.to_text()

    def to_html(self) -> str:
        return self.report.to_html()

    def _repr_html_(self) -> str:
        return self.to_html()


@dataclass(frozen=True)
class VerificationSession(Sequence[VerificationExecution]):
    """Complete result of one high-level ``verify(...)`` invocation."""

    source: str
    specification_path: Path | None
    schema: ModelSchema
    executions: tuple[VerificationExecution, ...]
    model: object | None = field(default=None, repr=False, compare=False)
    model_path: Path | None = None
    dataset_path: Path | None = None
    provenance: VerificationProvenanceContext | None = None
    anchor_resolutions: Mapping[str, ResolvedAnchorBinding] = field(
        default_factory=lambda: MappingProxyType({}),
        repr=False,
        compare=False,
    )

    def __len__(self) -> int:
        return len(self.executions)

    def __iter__(self) -> Iterator[VerificationExecution]:
        return iter(self.executions)

    @overload
    def __getitem__(self, index: int) -> VerificationExecution: ...

    @overload
    def __getitem__(self, index: slice) -> tuple[VerificationExecution, ...]: ...

    def __getitem__(
        self,
        index: int | slice,
    ) -> VerificationExecution | tuple[VerificationExecution, ...]:
        return self.executions[index]

    @property
    def reports(self) -> tuple[VerificationReport, ...]:
        return tuple(execution.report for execution in self.executions)

    @property
    def results(self) -> tuple[VerificationResult, ...]:
        return tuple(execution.result for execution in self.executions)

    @property
    def findings(self) -> tuple[VerificationFinding, ...]:
        return tuple(
            VerificationFinding(
                report=execution.report,
                task=execution.task,
                schema=self.schema,
                _model=self.model,
            )
            for execution in self.executions
        )

    @property
    def proved(self) -> tuple[VerificationFinding, ...]:
        return self._findings_with_status(VerificationStatus.PROVED)

    @property
    def counterexamples(self) -> tuple[VerificationFinding, ...]:
        return self._findings_with_status(VerificationStatus.COUNTEREXAMPLE)

    @property
    def witnesses(self) -> tuple[VerificationFinding, ...]:
        return self._findings_with_status(VerificationStatus.WITNESS)

    @property
    def no_witnesses(self) -> tuple[VerificationFinding, ...]:
        return self._findings_with_status(VerificationStatus.NO_WITNESS)

    @property
    def unknown(self) -> tuple[VerificationFinding, ...]:
        return self._findings_with_status(VerificationStatus.UNKNOWN)

    @property
    def first_counterexample(self) -> VerificationFinding | None:
        return self.counterexamples[0] if self.counterexamples else None

    @property
    def first_witness(self) -> VerificationFinding | None:
        return self.witnesses[0] if self.witnesses else None

    @property
    def has_failures(self) -> bool:
        """Return whether a property was violated or an existential had no witness."""

        return any(report.status in _FAILURE_STATUSES for report in self.reports)

    @property
    def has_unknown(self) -> bool:
        """Return whether at least one backend execution was inconclusive."""

        return any(
            report.status is VerificationStatus.UNKNOWN for report in self.reports
        )

    @property
    def is_successful(self) -> bool:
        """Return whether every property completed with a positive conclusion."""

        return bool(self.reports) and all(
            report.status in _SUCCESS_STATUSES for report in self.reports
        )

    @property
    def exit_code(self) -> int:
        """Return a CI-friendly exit code: 0 success, 1 failure, 2 inconclusive."""

        if self.has_failures:
            return 1
        if self.has_unknown:
            return 2
        return 0

    def to_records(self) -> list[dict[str, Any]]:
        """Return one neutral summary record per property."""

        records: list[dict[str, Any]] = []
        for report in self.reports:
            points = report_point_values(report)
            outputs_by_point = report_output_values_by_point(report)
            compatibility = report.numeric_compatibility
            report_payload = report.to_dict()
            execution_payload = report_payload["execution"]["backend_execution"]
            records.append(
                {
                    "property": report.property_index + 1,
                    "type": report.property_type.value,
                    "status": report.status.value,
                    "semantics": report.semantics.value,
                    "specification": report.specification,
                    "summary": report.summary,
                    "backend": report.backend.value,
                    "backend_status": report.backend_status,
                    "assumption_count": report.assumption_count,
                    "route_reason": report.route_reason,
                    "backend_execution_status": (
                        report.backend_execution.status
                        if report.backend_execution is not None
                        else None
                    ),
                    "backend_duration_ms": (
                        report.backend_execution.duration_ms
                        if report.backend_execution is not None
                        else None
                    ),
                    "backend_timeout_ms": (
                        report.backend_execution.timeout_ms
                        if report.backend_execution is not None
                        else None
                    ),
                    "backend_execution_reason": (
                        report.backend_execution.reason
                        if report.backend_execution is not None
                        else None
                    ),
                    "backend_native_reason": (
                        report.backend_execution.backend_reason
                        if report.backend_execution is not None
                        else None
                    ),
                    "backend_max_units": (
                        report.backend_execution.max_backend_units
                        if report.backend_execution is not None
                        else None
                    ),
                    "backend_max_memory_mb": (
                        report.backend_execution.max_memory_mb
                        if report.backend_execution is not None
                        else None
                    ),
                    "backend_deterministic_seed": (
                        report.backend_execution.deterministic_seed
                        if report.backend_execution is not None
                        else None
                    ),
                    "backend_options": (
                        dict(report.backend_execution.backend_options)
                        if report.backend_execution is not None
                        else {}
                    ),
                    "numeric_rule": (
                        compatibility.matched_rule_id
                        if compatibility is not None
                        else None
                    ),
                    "numeric_support_status": (
                        compatibility.support_status
                        if compatibility is not None
                        else None
                    ),
                    "numeric_classification": (
                        compatibility.classification
                        if compatibility is not None
                        else None
                    ),
                    "numeric_semantic_target": (
                        compatibility.semantic_target
                        if compatibility is not None
                        else None
                    ),
                    "numeric_conclusion_scope": (
                        compatibility.conclusion_scope
                        if compatibility is not None
                        else None
                    ),
                    "numeric_permitted_conclusions": (
                        compatibility.permitted_conclusions
                        if compatibility is not None
                        else ()
                    ),
                    "numeric_replay_required_for": (
                        compatibility.replay_required_for
                        if compatibility is not None
                        else ()
                    ),
                    "verification_fingerprint": (
                        report.provenance.verification_fingerprint
                        if report.provenance is not None
                        else None
                    ),
                    "input_fingerprint": (
                        report.provenance.input_fingerprint
                        if report.provenance is not None
                        else None
                    ),
                    "captured_at_utc": (
                        report.provenance.captured_at_utc
                        if report.provenance is not None
                        else None
                    ),
                    "inputs": _unique_group_values(points),
                    "outputs": _unique_group_values(outputs_by_point),
                    "points": points,
                    "outputs_by_point": outputs_by_point,
                    "backend_execution": execution_payload,
                    "numeric_compatibility": report_payload["numeric_compatibility"],
                    "provenance": report_payload["provenance"],
                    "point_evidence": report_payload["points"],
                    "assignments": report_payload["assignments"],
                    "model_evaluations": report_payload.get("model_evaluations", []),
                    "diagnostics": report_payload["diagnostics"],
                }
            )
        return records

    def to_dataframe(self) -> Any:
        """Return the session summary as a pandas data frame."""

        import pandas as pd

        return pd.DataFrame(self.to_records())

    def to_text(self, *, options: TextRenderOptions | None = None) -> str:
        """Render all reports using the shared terminal representation."""

        return render_verification_reports_text(self.reports, options=options)

    def print(
        self,
        *,
        file: TextIO | None = None,
        options: TextRenderOptions | None = None,
    ) -> None:
        """Print all reports to stdout or another text stream."""

        destination = file or sys.stdout
        rendered = self.to_text(options=options)
        if not _stream_accepts_text(destination, rendered):
            resolved_options = options or TextRenderOptions()
            rendered = self.to_text(
                options=replace(resolved_options, use_unicode=False),
            )
            if not _stream_accepts_text(destination, rendered):
                rendered = _escape_text_for_stream(destination, rendered)
        print(rendered, file=destination)

    def to_dict(self) -> dict[str, Any]:
        """Return the stable JSON-ready report collection."""

        return verification_reports_to_dict(self.reports)

    def to_json(self, *, indent: int | None = 2) -> str:
        """Serialize all reports using the stable collection contract."""

        return verification_reports_to_json(self.reports, indent=indent)

    def write_json(self, path: str | Path, *, indent: int | None = 2) -> Path:
        """Write all reports as one versioned JSON collection."""

        return write_verification_reports_json(self.reports, path, indent=indent)

    def to_html(self, *, options: HtmlRenderOptions | None = None) -> str:
        """Render all reports as a rich notebook-safe HTML fragment."""

        resolved = options or HtmlRenderOptions(
            collection_subtitle=(
                f"{self.schema.model_type} · target {self.schema.target} · "
                f"{len(self.reports)} properties"
            )
        )
        return render_verification_reports_html(self.reports, options=resolved)

    def write_html(
        self,
        path: str | Path,
        *,
        options: HtmlRenderOptions | None = None,
    ) -> Path:
        """Write all reports as one self-contained HTML document."""

        resolved = options or HtmlRenderOptions(
            collection_subtitle=(
                f"{self.schema.model_type} · target {self.schema.target} · "
                f"{len(self.reports)} properties"
            )
        )
        return write_verification_reports_html(
            self.reports,
            path,
            options=resolved,
        )

    def write_artifacts(
        self,
        directory: str | Path,
        *,
        formats: Iterable[str] = ("json", "html"),
        stem: str = "toetra-verification-report",
    ) -> dict[str, Path]:
        """Write several user-facing report formats into one directory."""

        output_directory = Path(directory)
        requested = tuple(dict.fromkeys(item.lower() for item in formats))
        unsupported = set(requested) - {"json", "html"}
        if unsupported:
            raise ValueError(
                "Unsupported report formats: " + ", ".join(sorted(unsupported))
            )

        written: dict[str, Path] = {}
        if "json" in requested:
            written["json"] = self.write_json(output_directory / f"{stem}.json")
        if "html" in requested:
            written["html"] = self.write_html(output_directory / f"{stem}.html")
        return written

    def _findings_with_status(
        self,
        status: VerificationStatus,
    ) -> tuple[VerificationFinding, ...]:
        return tuple(item for item in self.findings if item.status is status)

    def _repr_html_(self) -> str:
        """Return the rich representation automatically displayed by Jupyter."""

        return self.to_html()
