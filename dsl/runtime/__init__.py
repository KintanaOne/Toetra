"""High-level API for compiling, routing and executing FORML properties.

Application code should normally import the public facade from :mod:`forml`.
This module remains available for advanced integrations and compatibility.
"""

from dsl.runtime.api import verify
from dsl.provenance.model import VerificationProvenanceContext
from dsl.backends.execution import (
    BackendCancellationToken,
    BackendExecutionPolicy,
    BackendExecutionStatus,
    BackendResourceLimits,
    DEFAULT_BACKEND_TIMEOUT_MS,
)
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
from dsl.runtime.model_observer import (
    ModelObservation,
    ModelObserverRegistry,
    ModelRuntimeObserver,
)
from dsl.runtime.replay import CounterexampleReplay, EvaluationReplay
from dsl.runtime.session import (
    VerificationExecution,
    VerificationFinding,
    VerificationSession,
)

__all__ = [
    "VerificationProvenanceContext",
    "AnchorLookupRequest",
    "BackendCancellationToken",
    "BackendExecutionPolicy",
    "BackendExecutionStatus",
    "BackendResourceLimits",
    "DEFAULT_BACKEND_TIMEOUT_MS",
    "AnchorResolutionError",
    "AnchorResolver",
    "AnchorSource",
    "BackendRunnerNotRegisteredError",
    "BackendRunnerRegistry",
    "CounterexampleReplay",
    "ModelRuntimeObserver",
    "ModelObserverRegistry",
    "ModelObservation",
    "EvaluationReplay",
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
