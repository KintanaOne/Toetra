from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from dsl.backends.diagnostics import BackendResultDiagnostic
from dsl.backends.execution import BackendExecutionEvidence
from dsl.language.vocabulary.backends import EnumBackend


class VerificationStatus(str, Enum):
    """Backend-neutral interpretation of a FORML verification result."""

    PROVED = "proved"
    COUNTEREXAMPLE = "counterexample"
    WITNESS = "witness"
    NO_WITNESS = "no_witness"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class VerificationResult:
    """Normalized result returned by any FORML backend.

    Concrete backends keep their native status in ``backend_status`` and expose
    assignments through a backend-neutral mapping. Compatibility properties
    preserve the historical Z3-oriented names while callers migrate.
    """

    status: VerificationStatus
    backend: EnumBackend
    backend_status: str
    assignments: Mapping[str, Any] | None = None
    message: str = ""
    diagnostics: tuple[BackendResultDiagnostic, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)
    execution: BackendExecutionEvidence | None = None

    @property
    def solver_status(self) -> str:
        """Compatibility alias for the former Z3-specific result contract."""

        return self.backend_status

    @property
    def model(self) -> Mapping[str, Any] | None:
        """Compatibility alias for the former Z3-specific assignment mapping."""

        return self.assignments

    @property
    def has_assignments(self) -> bool:
        """Return whether the backend produced at least one assignment."""

        return bool(self.assignments)
