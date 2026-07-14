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


class UnsupportedScalarExpressionError(BackendTranslationError):
    """Raised when a scalar expression is outside the backend profile."""
