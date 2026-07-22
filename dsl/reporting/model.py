from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

from dsl.reporting.evaluations import ReportModelEvaluation
from dsl.reporting.values import exact_report_value, python_report_value
from dsl.provenance.model import ReportProvenance

from dsl.backends.diagnostics import BackendResultDiagnostic
from dsl.backends.results import VerificationStatus
from dsl.ir.ir2.enums import VerificationSemantics
from dsl.language.vocabulary.backends import EnumBackend
from dsl.language.vocabulary.properties import EnumProperty


class ReportAssignmentKind(str, Enum):
    """User-facing role of an assignment returned by a backend."""

    INPUT = "input"
    OUTPUT = "output"
    AUXILIARY = "auxiliary"


@dataclass(frozen=True)
class ReportAssignment:
    """One backend assignment normalized for reporting."""

    raw_name: str
    display_name: str
    value: Any
    kind: ReportAssignmentKind
    point_name: str | None = None
    binding_kind: str | None = None
    model_identity: str | None = None
    target_name: str | None = None
    output_name: str | None = None
    quantity_kind: str | None = None
    semantic_profile_id: str | None = None

    @property
    def exact_value(self) -> Any:
        """Return the exact backend value using standard Python numeric types."""

        return exact_report_value(self.value)

    @property
    def python_value(self) -> Any:
        """Return a convenient Python value for notebooks and application code."""

        return python_report_value(self.value)

    @property
    def field_name(self) -> str:
        """Return the unqualified feature or output name."""

        if self.target_name is not None:
            return self.target_name
        if self.kind is ReportAssignmentKind.INPUT and "." in self.display_name:
            return self.display_name.split(".", 1)[1]
        return self.display_name


@dataclass(frozen=True)
class ReportPointEvidence:
    """All public evidence associated with one semantic point."""

    name: str
    binding_kind: str
    inputs: tuple[ReportAssignment, ...] = ()
    outputs: tuple[ReportAssignment, ...] = ()
    provenance: Mapping[str, Any] | None = None

    @property
    def input_values(self) -> dict[str, Any]:
        return {item.field_name: item.python_value for item in self.inputs}

    @property
    def output_values(self) -> dict[str, Any]:
        return {item.field_name: item.python_value for item in self.outputs}


@dataclass(frozen=True)
class ReportScopeVariable:
    """One named variable declared by the property scope."""

    name: str
    role: str


@dataclass(frozen=True)
class ReportScope:
    """Backend-neutral scope summary used by all report renderers."""

    kind: str
    quantifier: str | None
    variables: tuple[ReportScopeVariable, ...]


@dataclass(frozen=True)
class ReportNumericCompatibility:
    """Public numeric route and semantic-guarantee evidence."""

    matched_rule_id: str | None
    support_status: str
    classification: str
    semantic_target: str
    conclusion_scope: str
    evidence_id: str | None
    framework_adapter_id: str
    framework_version: str | None
    model_family: str
    source_execution_profile_id: str
    model_encoder_id: str
    model_encoder_version: str
    backend_kind: str
    backend_adapter_id: str
    backend_profile_id: str
    backend_version: str | None
    property_numeric_requirements: tuple[str, ...]
    permitted_conclusions: tuple[str, ...]
    replay_required_for: tuple[str, ...]
    assumptions_and_preconditions: tuple[str, ...]
    compatibility_diagnostics: tuple[str, ...]
    documentation_reference: str | None

    @property
    def source_route(self) -> str:
        framework = self.framework_adapter_id
        if self.framework_version is not None:
            framework += f"@{self.framework_version}"
        return (
            f"{framework} / {self.model_family} / "
            f"{self.source_execution_profile_id}"
        )

    @property
    def backend_route(self) -> str:
        backend = self.backend_adapter_id
        if self.backend_version is not None:
            backend += f"@{self.backend_version}"
        return f"{self.backend_kind} / {backend} / {self.backend_profile_id}"


@dataclass(frozen=True)
class ReportBackendExecution:
    """Portable execution-policy and termination evidence."""

    status: str
    duration_ms: float
    reason: str | None
    backend_reason: str | None
    timeout_ms: int | None
    max_backend_units: int | None
    max_memory_mb: int | None
    deterministic_seed: int | None
    backend_options: Mapping[str, bool | int | float | str]


@dataclass(frozen=True)
class VerificationReport:
    """User-facing representation of one completed FORML verification task.

    The report contains normalized data only. Text, JSON and HTML renderers are
    separate concerns and will consume this model without importing a backend.
    """

    property_index: int
    property_type: EnumProperty
    semantics: VerificationSemantics
    scope: ReportScope
    specification: str
    backend: EnumBackend
    backend_status: str
    status: VerificationStatus
    summary: str
    assignments: tuple[ReportAssignment, ...]
    diagnostics: tuple[BackendResultDiagnostic, ...]
    assumption_count: int
    route_reason: str
    points: tuple[ReportPointEvidence, ...] = ()
    numeric_compatibility: ReportNumericCompatibility | None = None
    backend_execution: ReportBackendExecution | None = None
    provenance: ReportProvenance | None = None
    model_evaluations: tuple[ReportModelEvaluation, ...] = ()

    @property
    def inputs(self) -> tuple[ReportAssignment, ...]:
        return tuple(
            item for item in self.assignments if item.kind is ReportAssignmentKind.INPUT
        )

    @property
    def outputs(self) -> tuple[ReportAssignment, ...]:
        return tuple(
            item
            for item in self.assignments
            if item.kind is ReportAssignmentKind.OUTPUT
        )

    @property
    def auxiliary_assignments(self) -> tuple[ReportAssignment, ...]:
        return tuple(
            item
            for item in self.assignments
            if item.kind is ReportAssignmentKind.AUXILIARY
        )

    @property
    def qualified_input_values(self) -> dict[str, Any]:
        """Return input assignments keyed by their qualified FORML names."""

        return {item.display_name: item.python_value for item in self.inputs}

    @property
    def point_values(self) -> dict[str, dict[str, Any]]:
        """Return input values grouped by exact point identity."""

        return {point.name: point.input_values for point in self.points if point.inputs}

    @property
    def output_values_by_point(self) -> dict[str, dict[str, Any]]:
        """Return model outputs grouped by evaluation point."""

        return {
            point.name: point.output_values for point in self.points if point.outputs
        }

    @property
    def input_values(self) -> dict[str, Any]:
        """Return the unique point input vector, rejecting ambiguous flattening."""

        grouped = self.point_values
        if len(grouped) > 1:
            raise ValueError(
                "Input values belong to multiple points. Use 'point_values' instead."
            )
        if grouped:
            return next(iter(grouped.values()))
        return {}

    @property
    def model_evaluations_by_point(
        self,
    ) -> dict[str, tuple[ReportModelEvaluation, ...]]:
        """Return enriched model evaluations grouped by exact point identity."""

        grouped: dict[str, list[ReportModelEvaluation]] = {}
        for evaluation in self.model_evaluations:
            grouped.setdefault(evaluation.point_name, []).append(evaluation)
        return {name: tuple(items) for name, items in grouped.items()}

    @property
    def output_values(self) -> dict[str, Any]:
        """Return the unique point outputs, rejecting ambiguous flattening."""

        grouped = self.output_values_by_point
        if len(grouped) > 1:
            raise ValueError(
                "Model outputs belong to multiple points. "
                "Use 'output_values_by_point' instead."
            )
        if grouped:
            return next(iter(grouped.values()))
        return {}

    @property
    def has_failure(self) -> bool:
        """Return whether the report contains a concrete property violation."""

        return self.status is VerificationStatus.COUNTEREXAMPLE

    def to_text(self) -> str:
        """Render this report using the default user-facing text renderer."""

        from dsl.reporting.text import render_verification_report_text

        return render_verification_report_text(self)

    def to_dict(self) -> dict[str, Any]:
        """Return the versioned JSON-ready representation of this report."""

        from dsl.reporting.json import verification_report_to_dict

        return verification_report_to_dict(self)

    def to_json(self, *, indent: int | None = 2) -> str:
        """Serialize this report using the stable FORML JSON contract."""

        from dsl.reporting.json import verification_report_to_json

        return verification_report_to_json(self, indent=indent)

    def write_json(self, path: str | Path, *, indent: int | None = 2) -> Path:
        """Write this report to disk using the stable FORML JSON contract."""

        from dsl.reporting.json import write_verification_report_json

        return write_verification_report_json(self, path, indent=indent)

    def to_html(self) -> str:
        """Render this report as a notebook-safe HTML fragment."""

        from dsl.reporting.html import render_verification_report_html

        return render_verification_report_html(self)

    def write_html(self, path: str | Path) -> Path:
        """Write this report as a self-contained HTML document."""

        from dsl.reporting.html import write_verification_report_html

        return write_verification_report_html(self, path)

    def _repr_html_(self) -> str:
        """Return the rich representation automatically used by Jupyter."""

        return self.to_html()
