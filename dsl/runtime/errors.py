"""Errors raised by the high-level FORML verification runtime."""


class VerificationRuntimeError(RuntimeError):
    """Base error for user-facing runtime orchestration failures."""


class VerificationConfigurationError(VerificationRuntimeError, ValueError):
    """Raised when verification inputs are ambiguous or inconsistent."""


class BackendRunnerNotRegisteredError(VerificationRuntimeError):
    """Raised when routing succeeds but no executor exists for the backend."""


class ReplayUnavailableError(VerificationRuntimeError):
    """Raised when a formal assignment cannot be replayed on a model."""


class AnchorResolutionError(VerificationRuntimeError):
    """Raised when a referenced anchor cannot be resolved soundly."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        anchor_name: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.anchor_name = anchor_name
