from dsl.backends.execution import BackendExecutionEvidence


class BackendError(Exception):
    """Base class for backend routing/translation errors."""


class BackendRoutingError(BackendError):
    """Raised when no backend can be selected for a verification task."""


class BackendNotRegisteredError(BackendRoutingError):
    """Raised when a requested backend has not been registered."""


class NoCompatibleBackendError(BackendRoutingError):
    """Raised when registered backends do not satisfy IR2 requirements."""


class BackendTranslationError(BackendError):
    """Raised when an IR task cannot be translated soundly."""


class UnsupportedBackendRequirementsError(BackendTranslationError):
    """Raised when direct translation bypasses routing capability checks."""


class BackendSymbolCollisionError(BackendTranslationError):
    """Raised when two structured identities project to one solver symbol."""


class UnsupportedScalarExpressionError(BackendTranslationError):
    """Raised when a scalar expression is outside the backend profile."""


class BackendExecutionError(BackendError, RuntimeError):
    """Raised when a backend fails technically rather than logically."""

    def __init__(
        self,
        message: str,
        *,
        backend: str,
        evidence: BackendExecutionEvidence,
    ) -> None:
        super().__init__(message)
        self.backend = backend
        self.evidence = evidence
