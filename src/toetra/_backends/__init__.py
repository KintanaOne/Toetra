"""Backend routing and execution primitives.

This package is backend-neutral at the top level. Concrete backends such as Z3
live in subpackages and expose the common ``VerificationResult`` contract.
"""

from toetra._backends.base import BackendRunner, BackendTranslator
from toetra._backends.errors import BackendExecutionError
from toetra._backends.capabilities import BackendCapabilities
from toetra._backends.defaults import create_default_backend_registry
from toetra._backends.execution import (
    BackendCancellationToken,
    BackendExecutionCapabilities,
    BackendExecutionEvidence,
    BackendExecutionPolicy,
    BackendExecutionPolicySnapshot,
    BackendExecutionStatus,
    BackendResourceLimits,
    DEFAULT_BACKEND_TIMEOUT_MS,
)
from toetra._backends.diagnostics import (
    BackendDiagnosticSeverity,
    BackendResultDiagnostic,
)
from toetra._backends.registry import BackendRegistry
from toetra._backends.results import VerificationResult, VerificationStatus
from toetra._backends.router import BackendRoute, BackendRouter

__all__ = [
    "BackendCapabilities",
    "BackendCancellationToken",
    "BackendExecutionCapabilities",
    "BackendExecutionError",
    "BackendExecutionEvidence",
    "BackendExecutionPolicy",
    "BackendExecutionPolicySnapshot",
    "BackendExecutionStatus",
    "BackendResourceLimits",
    "DEFAULT_BACKEND_TIMEOUT_MS",
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
