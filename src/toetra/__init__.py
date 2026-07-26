"""Supported public Python API for Toetra model verification.

Only names listed in :data:`__all__` belong to the stable V1 Python contract.
Modules beneath ``toetra._*`` are private implementation details.
"""

from toetra._backends.results import VerificationStatus
from toetra._reporting.model import VerificationReport
from toetra._runtime.api import verify
from toetra._runtime.errors import (
    ReplayUnavailableError,
    VerificationConfigurationError,
    VerificationRuntimeError,
)
from toetra._runtime.replay import CounterexampleReplay
from toetra._runtime.session import VerificationFinding, VerificationSession

__all__ = (
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
