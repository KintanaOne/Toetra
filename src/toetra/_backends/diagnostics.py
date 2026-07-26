from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BackendDiagnosticSeverity(str, Enum):
    """Severity attached to a backend execution diagnostic."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class BackendResultDiagnostic:
    """Structured diagnostic emitted while interpreting a backend result."""

    code: str
    severity: BackendDiagnosticSeverity
    message: str
