from __future__ import annotations

import pytest

from toetra import (
    ReplayUnavailableError,
    VerificationConfigurationError,
    VerificationRuntimeError,
)
from toetra._runtime.errors import (
    AnchorResolutionError,
    BackendRunnerNotRegisteredError,
)


@pytest.mark.parametrize(
    ("error_type", "code", "stage"),
    [
        (
            VerificationRuntimeError,
            "VERIFICATION_RUNTIME_ERROR",
            "runtime",
        ),
        (
            VerificationConfigurationError,
            "VERIFICATION_CONFIGURATION_ERROR",
            "configuration",
        ),
        (
            ReplayUnavailableError,
            "REPLAY_UNAVAILABLE",
            "replay",
        ),
        (
            BackendRunnerNotRegisteredError,
            "BACKEND_RUNNER_NOT_REGISTERED",
            "runtime",
        ),
    ],
)
def test_public_error_families_expose_stable_diagnostic_defaults(
    error_type: type[VerificationRuntimeError],
    code: str,
    stage: str,
) -> None:
    error = error_type("failure")

    assert str(error) == "failure"
    assert error.message == "failure"
    assert error.code == code
    assert error.stage == stage
    assert error.hint is None
    assert error.path is None
    assert error.line is None
    assert error.column is None


def test_public_error_preserves_structured_diagnostic_context() -> None:
    error = VerificationConfigurationError(
        "Unexpected token",
        code="SPECIFICATION_SYNTAX_ERROR",
        stage="syntax",
        hint="Check the quantified property.",
        path="policy.toetra",
        line=7,
        column=12,
    )

    assert error.code == "SPECIFICATION_SYNTAX_ERROR"
    assert error.stage == "syntax"
    assert error.hint == "Check the quantified property."
    assert error.path == "policy.toetra"
    assert error.line == 7
    assert error.column == 12


def test_anchor_error_keeps_its_existing_specific_context() -> None:
    error = AnchorResolutionError(
        "Anchor not found",
        code="ANCHOR_NOT_FOUND",
        anchor_name="baseline",
        hint="Check the anchor key and source.",
    )

    assert error.code == "ANCHOR_NOT_FOUND"
    assert error.stage == "anchor"
    assert error.anchor_name == "baseline"
    assert error.hint == "Check the anchor key and source."
