from __future__ import annotations

import pytest

from dsl.backends.execution import (
    BackendCancellationToken,
    BackendExecutionCapabilities,
    BackendExecutionPolicy,
    BackendResourceLimits,
    DEFAULT_BACKEND_TIMEOUT_MS,
)


def test_default_policy_enforces_a_finite_backend_timeout() -> None:
    policy = BackendExecutionPolicy()

    assert policy.timeout_ms == DEFAULT_BACKEND_TIMEOUT_MS
    assert policy.timeout_ms is not None
    assert policy.timeout_ms > 0


def test_policy_snapshot_is_serializable_and_excludes_cancellation_state() -> None:
    token = BackendCancellationToken()
    policy = BackendExecutionPolicy(
        timeout_ms=1_500,
        resources=BackendResourceLimits(
            max_backend_units=200,
            max_memory_mb=64,
        ),
        deterministic_seed=7,
        cancellation_token=token,
        backend_options={"phase_selection": 2},
    )

    snapshot = policy.snapshot()

    assert snapshot.timeout_ms == 1_500
    assert snapshot.max_backend_units == 200
    assert snapshot.max_memory_mb == 64
    assert snapshot.deterministic_seed == 7
    assert dict(snapshot.backend_options) == {"phase_selection": 2}
    assert not hasattr(snapshot, "cancellation_token")


def test_cancellation_token_is_thread_safe_and_monotonic() -> None:
    token = BackendCancellationToken()

    assert not token.is_cancelled()
    token.cancel()
    assert token.is_cancelled()
    token.cancel()
    assert token.is_cancelled()


@pytest.mark.parametrize(
    "policy",
    (
        BackendExecutionPolicy(timeout_ms=None),
        BackendExecutionPolicy(resources=BackendResourceLimits(max_backend_units=10)),
        BackendExecutionPolicy(resources=BackendResourceLimits(max_memory_mb=32)),
        BackendExecutionPolicy(deterministic_seed=1),
        BackendExecutionPolicy(backend_options={"custom": True}),
    ),
)
def test_execution_capabilities_fail_closed_for_unsupported_controls(
    policy: BackendExecutionPolicy,
) -> None:
    capabilities = BackendExecutionCapabilities(
        supports_timeout=False,
        supports_cancellation=False,
        supports_max_backend_units=False,
        supports_max_memory=False,
        supports_deterministic_seed=False,
        supported_backend_options=frozenset(),
    )

    incompatibilities = capabilities.incompatibilities(policy)

    if policy.timeout_ms is None and not any(
        (
            policy.resources.max_backend_units,
            policy.resources.max_memory_mb,
            policy.deterministic_seed,
            policy.backend_options,
        )
    ):
        assert incompatibilities == ()
    else:
        assert incompatibilities


def test_execution_policy_rejects_invalid_limits_and_options() -> None:
    with pytest.raises(ValueError, match="timeout_ms"):
        BackendExecutionPolicy(timeout_ms=0)
    with pytest.raises(ValueError, match="max_memory_mb"):
        BackendResourceLimits(max_memory_mb=0)
    with pytest.raises(ValueError, match="deterministic_seed"):
        BackendExecutionPolicy(deterministic_seed=-1)
    with pytest.raises(ValueError, match="must not be empty"):
        BackendExecutionPolicy(backend_options={" ": 1})
    with pytest.raises(ValueError, match="must be finite"):
        BackendExecutionPolicy(backend_options={"ratio": float("inf")})
