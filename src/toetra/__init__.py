"""Public Python facade for Toetra model verification.

The compiler, IR and backend packages remain available for advanced use, but
normal application code should start here.
"""

from toetra._backends.results import VerificationStatus
from toetra._reporting import VerificationReport
from toetra._runtime import (
    CounterexampleReplay,
    ReplayUnavailableError,
    VerificationConfigurationError,
    VerificationFinding,
    VerificationRuntimeError,
    VerificationSession,
    verify,
)

__all__ = [
    "CounterexampleReplay",
    "ReplayUnavailableError",
    "VerificationConfigurationError",
    "VerificationFinding",
    "VerificationReport",
    "VerificationRuntimeError",
    "VerificationSession",
    "VerificationStatus",
    "verify",
]
