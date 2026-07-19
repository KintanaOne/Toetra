from __future__ import annotations

import math
import threading
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Mapping, Protocol, TypeAlias

BackendOptionValue: TypeAlias = bool | int | float | str

DEFAULT_BACKEND_TIMEOUT_MS = 30_000


class BackendExecutionStatus(str, Enum):
    """Backend-neutral termination status for one execution attempt."""

    SAT = "sat"
    UNSAT = "unsat"
    UNKNOWN = "unknown"
    TIMEOUT = "timeout"
    RESOURCE_LIMIT = "resource_limit"
    CANCELLED = "cancelled"
    ERROR = "error"


class CancellationToken(Protocol):
    """Cooperative cancellation contract understood by backend adapters."""

    def is_cancelled(self) -> bool: ...


class BackendCancellationToken:
    """Thread-safe cancellation token suitable for local backend execution."""

    def __init__(self) -> None:
        self._event = threading.Event()

    def cancel(self) -> None:
        self._event.set()

    def is_cancelled(self) -> bool:
        return self._event.is_set()


@dataclass(frozen=True)
class BackendResourceLimits:
    """Portable resource limits interpreted by each backend adapter.

    ``max_backend_units`` is an abstract deterministic work budget. A concrete
    adapter maps it to its closest native resource counter (for example Z3's
    ``rlimit``). ``max_memory_mb`` is a process/backend memory ceiling when the
    adapter exposes one.
    """

    max_backend_units: int | None = None
    max_memory_mb: int | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("max_backend_units", self.max_backend_units),
            ("max_memory_mb", self.max_memory_mb),
        ):
            if value is not None and value <= 0:
                raise ValueError(f"{name} must be a strictly positive integer")


@dataclass(frozen=True)
class BackendExecutionPolicy:
    """Backend-neutral execution policy applied to every verification task."""

    timeout_ms: int | None = DEFAULT_BACKEND_TIMEOUT_MS
    resources: BackendResourceLimits = field(default_factory=BackendResourceLimits)
    deterministic_seed: int | None = None
    cancellation_token: CancellationToken | None = field(
        default=None,
        repr=False,
        compare=False,
    )
    backend_options: Mapping[str, BackendOptionValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.timeout_ms is not None and self.timeout_ms <= 0:
            raise ValueError("timeout_ms must be a strictly positive integer or None")
        if self.deterministic_seed is not None and self.deterministic_seed < 0:
            raise ValueError("deterministic_seed must be non-negative or None")
        normalized: dict[str, BackendOptionValue] = {}
        for raw_name, value in self.backend_options.items():
            name = str(raw_name).strip()
            if not name:
                raise ValueError("backend option names must not be empty")
            if isinstance(value, float) and not math.isfinite(value):
                raise ValueError(f"backend option {name!r} must be finite")
            normalized[name] = value
        object.__setattr__(self, "backend_options", MappingProxyType(normalized))

    @property
    def cancelled(self) -> bool:
        token = self.cancellation_token
        return token is not None and token.is_cancelled()

    def snapshot(self) -> BackendExecutionPolicySnapshot:
        return BackendExecutionPolicySnapshot(
            timeout_ms=self.timeout_ms,
            max_backend_units=self.resources.max_backend_units,
            max_memory_mb=self.resources.max_memory_mb,
            deterministic_seed=self.deterministic_seed,
            backend_options=dict(self.backend_options),
        )


@dataclass(frozen=True)
class BackendExecutionPolicySnapshot:
    """Serializable, token-free view of the policy used for one result."""

    timeout_ms: int | None
    max_backend_units: int | None
    max_memory_mb: int | None
    deterministic_seed: int | None
    backend_options: Mapping[str, BackendOptionValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "backend_options",
            MappingProxyType(dict(self.backend_options)),
        )


@dataclass(frozen=True)
class BackendExecutionEvidence:
    """Portable evidence describing how one backend attempt terminated."""

    status: BackendExecutionStatus
    duration_ms: float
    policy: BackendExecutionPolicySnapshot
    reason: str | None = None
    backend_reason: str | None = None

    def __post_init__(self) -> None:
        if not math.isfinite(self.duration_ms) or self.duration_ms < 0:
            raise ValueError("duration_ms must be a finite non-negative value")


@dataclass(frozen=True)
class BackendExecutionCapabilities:
    """Execution controls that one backend adapter promises to enforce."""

    supports_timeout: bool = False
    supports_cancellation: bool = False
    supports_max_backend_units: bool = False
    supports_max_memory: bool = False
    supports_deterministic_seed: bool = False
    supported_backend_options: frozenset[str] | None = frozenset()

    def incompatibilities(
        self,
        policy: BackendExecutionPolicy,
    ) -> tuple[str, ...]:
        reasons: list[str] = []
        if policy.timeout_ms is not None and not self.supports_timeout:
            reasons.append("timeout")
        if policy.cancellation_token is not None and not self.supports_cancellation:
            reasons.append("cancellation")
        if (
            policy.resources.max_backend_units is not None
            and not self.supports_max_backend_units
        ):
            reasons.append("backend resource units")
        if policy.resources.max_memory_mb is not None and not self.supports_max_memory:
            reasons.append("memory limit")
        if (
            policy.deterministic_seed is not None
            and not self.supports_deterministic_seed
        ):
            reasons.append("deterministic seed")
        supported = self.supported_backend_options
        if supported is not None:
            unsupported_options = set(policy.backend_options) - supported
            if unsupported_options:
                reasons.append(
                    "backend options {" + ", ".join(sorted(unsupported_options)) + "}"
                )
        return tuple(reasons)
