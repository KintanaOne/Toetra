from __future__ import annotations

from forml import (
    CounterexampleReplay,
    ReplayUnavailableError,
    VerificationFinding,
    VerificationReport,
    VerificationSession,
    VerificationStatus,
    verify,
)


def test_public_facade_exposes_the_normal_user_api() -> None:
    assert callable(verify)
    assert VerificationStatus.PROVED.value == "proved"
    assert VerificationSession.__name__ == "VerificationSession"
    assert VerificationFinding.__name__ == "VerificationFinding"
    assert VerificationReport.__name__ == "VerificationReport"
    assert CounterexampleReplay.__name__ == "CounterexampleReplay"
    assert issubclass(ReplayUnavailableError, RuntimeError)
