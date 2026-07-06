class BackendError(Exception):
    """Base class for backend routing/translation errors."""


class BackendRoutingError(BackendError):
    """Raised when no backend can be selected for a verification task."""


class BackendNotRegisteredError(BackendRoutingError):
    """Raised when a requested backend has not been registered."""


class NoCompatibleBackendError(BackendRoutingError):
    """Raised when registered backends do not satisfy IR2 requirements."""
