from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from dsl.reporting.values import exact_report_value, python_report_value

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

        if self.kind is ReportAssignmentKind.INPUT and "." in self.display_name:
            return self.display_name.split(".", 1)[1]
        return self.display_name


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
    def input_values(self) -> dict[str, Any]:
        """Return input assignments keyed by unqualified feature names."""

        values: dict[str, Any] = {}
        for item in self.inputs:
            if item.field_name in values:
                raise ValueError(
                    "Input feature names are ambiguous without their scope entity: "
                    f"{item.field_name!r}. Use 'qualified_input_values' instead."
                )
            values[item.field_name] = item.python_value
        return values

    @property
    def output_values(self) -> dict[str, Any]:
        """Return model outputs keyed by their public target names."""

        return {item.field_name: item.python_value for item in self.outputs}

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
