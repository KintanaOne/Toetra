"""Public Python facade for FORML model verification.

The compiler, IR and backend packages remain available for advanced use, but
normal application code should start here.
"""

from dsl.backends.results import VerificationStatus
from dsl.reporting import VerificationReport
from dsl.runtime import (
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
