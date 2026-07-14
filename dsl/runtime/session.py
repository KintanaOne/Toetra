from __future__ import annotations

import sys
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TextIO, overload

from dsl.backends.results import VerificationResult, VerificationStatus
from dsl.backends.router import BackendRoute
from dsl.ir.ir2.nodes import VerificationTaskIR2
from dsl.reporting import (
    HtmlRenderOptions,
    TextRenderOptions,
    VerificationReport,
    render_verification_reports_html,
    render_verification_reports_text,
    verification_reports_to_dict,
    verification_reports_to_json,
    write_verification_reports_html,
    write_verification_reports_json,
)
from model.schema.model_schema import ModelSchema

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


@dataclass(frozen=True)
class VerificationExecution:
    """One compiled, routed, executed and reported FORML property."""

    task: VerificationTaskIR2
    route: BackendRoute
    result: VerificationResult
    report: VerificationReport


@dataclass(frozen=True)
class VerificationSession(Sequence[VerificationExecution]):
    """Complete result of one high-level ``verify(...)`` invocation."""

    source: str
    specification_path: Path | None
    schema: ModelSchema
    executions: tuple[VerificationExecution, ...]

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
        print(self.to_text(options=options), file=destination)

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

    def _repr_html_(self) -> str:
        """Return the rich representation automatically displayed by Jupyter."""

        return self.to_html()
