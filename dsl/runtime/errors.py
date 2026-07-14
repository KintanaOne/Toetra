"""Errors raised by the high-level FORML verification runtime."""


class VerificationRuntimeError(RuntimeError):
    """Base error for user-facing runtime orchestration failures."""


class VerificationConfigurationError(VerificationRuntimeError, ValueError):
    """Raised when verification inputs are ambiguous or inconsistent."""


class BackendRunnerNotRegisteredError(VerificationRuntimeError):
    """Raised when routing succeeds but no executor exists for the backend."""
