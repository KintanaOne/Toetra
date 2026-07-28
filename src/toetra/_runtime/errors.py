"""Errors raised by the high-level Toetra verification runtime."""


class VerificationRuntimeError(RuntimeError):
    """Base error for user-facing verification failures.

    Concrete private exceptions may change, but public callers can rely on the
    structured diagnostic attributes defined here.
    """

    _default_code = "VERIFICATION_RUNTIME_ERROR"
    _default_stage = "runtime"

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        stage: str | None = None,
        hint: str | None = None,
        path: str | None = None,
        line: int | None = None,
        column: int | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code or self._default_code
        self.stage = stage or self._default_stage
        self.hint = hint
        self.path = path
        self.line = line
        self.column = column


class VerificationConfigurationError(VerificationRuntimeError, ValueError):
    """Raised when verification inputs are invalid, ambiguous, or inconsistent."""

    _default_code = "VERIFICATION_CONFIGURATION_ERROR"
    _default_stage = "configuration"


class BackendRunnerNotRegisteredError(VerificationRuntimeError):
    """Raised when routing succeeds but no executor exists for the backend."""

    _default_code = "BACKEND_RUNNER_NOT_REGISTERED"
    _default_stage = "runtime"


class ReplayUnavailableError(VerificationRuntimeError):
    """Raised when a formal assignment cannot be replayed on a model."""

    _default_code = "REPLAY_UNAVAILABLE"
    _default_stage = "replay"


class AnchorResolutionError(VerificationRuntimeError):
    """Raised when a referenced anchor cannot be resolved soundly."""

    _default_stage = "anchor"

    def __init__(
        self,
        message: str,
        *,
        code: str,
        anchor_name: str | None = None,
        hint: str | None = None,
        path: str | None = None,
        line: int | None = None,
        column: int | None = None,
    ) -> None:
        super().__init__(
            message,
            code=code,
            hint=hint,
            path=path,
            line=line,
            column=column,
        )
        self.anchor_name = anchor_name
