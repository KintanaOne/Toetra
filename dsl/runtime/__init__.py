"""High-level API for compiling, routing and executing FORML properties.

Application code should normally import the public facade from :mod:`forml`.
This module remains available for advanced integrations and compatibility.
"""

from dsl.runtime.api import verify
from dsl.runtime.backends import (
    BackendRunnerRegistry,
    create_default_backend_runner_registry,
)
from dsl.runtime.errors import (
    BackendRunnerNotRegisteredError,
    ReplayUnavailableError,
    VerificationConfigurationError,
    VerificationRuntimeError,
)
from dsl.runtime.replay import CounterexampleReplay
from dsl.runtime.session import (
    VerificationExecution,
    VerificationFinding,
    VerificationSession,
)

__all__ = [
    "BackendRunnerNotRegisteredError",
    "BackendRunnerRegistry",
    "CounterexampleReplay",
    "ReplayUnavailableError",
    "VerificationConfigurationError",
    "VerificationExecution",
    "VerificationFinding",
    "VerificationRuntimeError",
    "VerificationSession",
    "create_default_backend_runner_registry",
    "verify",
]
