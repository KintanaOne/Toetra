"""High-level API for compiling, routing and executing FORML properties.

Application code should normally import the public facade from :mod:`forml`.
This module remains available for advanced integrations and compatibility.
"""

from dsl.runtime.api import verify
from dsl.runtime.anchors import (
    AnchorLookupRequest,
    AnchorResolver,
    AnchorSource,
    DataFrameAnchorResolver,
)
from dsl.runtime.backends import (
    BackendRunnerRegistry,
    create_default_backend_runner_registry,
)
from dsl.runtime.errors import (
    AnchorResolutionError,
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
    "AnchorLookupRequest",
    "AnchorResolutionError",
    "AnchorResolver",
    "AnchorSource",
    "BackendRunnerNotRegisteredError",
    "BackendRunnerRegistry",
    "CounterexampleReplay",
    "DataFrameAnchorResolver",
    "ReplayUnavailableError",
    "VerificationConfigurationError",
    "VerificationExecution",
    "VerificationFinding",
    "VerificationRuntimeError",
    "VerificationSession",
    "create_default_backend_runner_registry",
    "verify",
]
