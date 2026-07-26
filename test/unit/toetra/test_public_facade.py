from __future__ import annotations

import toetra as toetra_module
from toetra import (
    CounterexampleReplay,
    ReplayUnavailableError,
    VerificationConfigurationError,
    VerificationFinding,
    VerificationReport,
    VerificationRuntimeError,
    VerificationSession,
    VerificationStatus,
    verify,
)

EXPECTED_PUBLIC_API = (
    "CounterexampleReplay",
    "ReplayUnavailableError",
    "VerificationConfigurationError",
    "VerificationFinding",
    "VerificationReport",
    "VerificationRuntimeError",
    "VerificationSession",
    "VerificationStatus",
    "verify",
)


def test_public_facade_exports_exactly_the_v1_api() -> None:
    assert toetra_module.__all__ == EXPECTED_PUBLIC_API
    exported = {name: getattr(toetra_module, name) for name in toetra_module.__all__}
    assert tuple(exported) == EXPECTED_PUBLIC_API


def test_public_facade_exposes_the_normal_user_api() -> None:
    assert callable(verify)
    assert VerificationStatus.PROVED.value == "proved"
    assert VerificationSession.__name__ == "VerificationSession"
    assert VerificationFinding.__name__ == "VerificationFinding"
    assert VerificationReport.__name__ == "VerificationReport"
    assert CounterexampleReplay.__name__ == "CounterexampleReplay"
    assert issubclass(ReplayUnavailableError, RuntimeError)
    assert issubclass(VerificationConfigurationError, RuntimeError)
    assert issubclass(VerificationRuntimeError, RuntimeError)
