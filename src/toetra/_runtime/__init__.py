"""High-level API for compiling, routing and executing Toetra properties.

Application code should normally import the public facade from :mod:`toetra`.
This module remains available for advanced integrations and compatibility.
"""

from toetra._runtime.api import verify
from toetra._provenance.model import VerificationProvenanceContext
from toetra._backends.execution import (
    BackendCancellationToken,
    BackendExecutionPolicy,
    BackendExecutionStatus,
    BackendResourceLimits,
    DEFAULT_BACKEND_TIMEOUT_MS,
)
from toetra._runtime.anchors import (
    AnchorLookupRequest,
    AnchorResolver,
    AnchorSource,
    DataFrameAnchorResolver,
)
from toetra._runtime.backends import (
    BackendRunnerRegistry,
    create_default_backend_runner_registry,
)
from toetra._runtime.errors import (
    AnchorResolutionError,
    BackendRunnerNotRegisteredError,
    ReplayUnavailableError,
    VerificationConfigurationError,
    VerificationRuntimeError,
)
from toetra._runtime.model_observer import (
    ModelObservation,
    ModelObserverRegistry,
    ModelRuntimeObserver,
)
from toetra._runtime.replay import CounterexampleReplay, EvaluationReplay
from toetra._runtime.session import (
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
