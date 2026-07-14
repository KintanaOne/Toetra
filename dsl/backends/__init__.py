"""Backend routing and execution primitives.

This package is backend-neutral at the top level. Concrete backends such as Z3
live in subpackages and expose the common ``VerificationResult`` contract.
"""

from dsl.backends.base import BackendRunner, BackendTranslator
from dsl.backends.capabilities import BackendCapabilities
from dsl.backends.defaults import create_default_backend_registry
from dsl.backends.diagnostics import (
    BackendDiagnosticSeverity,
    BackendResultDiagnostic,
)
from dsl.backends.registry import BackendRegistry
from dsl.backends.results import VerificationResult, VerificationStatus
from dsl.backends.router import BackendRoute, BackendRouter

__all__ = [
    "BackendCapabilities",
    "BackendDiagnosticSeverity",
    "BackendResultDiagnostic",
    "BackendRegistry",
    "BackendRoute",
    "BackendRouter",
    "BackendRunner",
    "BackendTranslator",
    "VerificationResult",
    "VerificationStatus",
    "create_default_backend_registry",
]
