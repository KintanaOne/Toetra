# Backend Execution Contract

> Status: Implemented  
> Source of truth: `toetra._backends.execution`

## Purpose

The execution contract is independent from backend logic and numeric
compatibility.

```text
IR2 capability check
+ numeric compatibility check
+ execution-policy capability check
→ selected backend route
→ backend execution
→ logical result + execution evidence
```

A backend can understand the IR2 task and still be rejected because it cannot
enforce the requested operational policy.

## Public policy

```python
from toetra._backends.execution import (
    BackendCancellationToken,
    BackendExecutionPolicy,
    BackendResourceLimits,
)

cancellation = BackendCancellationToken()
policy = BackendExecutionPolicy(
    timeout_ms=10_000,
    resources=BackendResourceLimits(
        max_backend_units=500_000,
        max_memory_mb=512,
    ),
    deterministic_seed=7,
    cancellation_token=cancellation,
)

session = verify(specification, execution_policy=policy)
```

The default policy uses a 30,000 ms timeout. `timeout_ms=None` explicitly opts
out of the deadline.

## Capability declaration

A backend adapter declares:

```python
BackendExecutionCapabilities(
    supports_timeout=True,
    supports_cancellation=True,
    supports_max_backend_units=True,
    supports_max_memory=True,
    supports_deterministic_seed=True,
    supported_backend_options=None,
)
```

`None` for `supported_backend_options` means the adapter owns validation of
arbitrary native options. A finite set is an allowlist. The empty set rejects
all adapter-specific options.

Routing fails closed when a requested control is unsupported.

## Status separation

`VerificationStatus` answers the Toetra question:

```text
proved / counterexample / witness / no_witness / unknown
```

`BackendExecutionStatus` answers how the backend attempt terminated:

```text
sat / unsat / unknown / timeout / resource_limit / cancelled / error
```

These dimensions must not be merged. For example:

```text
VerificationStatus.UNKNOWN
BackendExecutionStatus.TIMEOUT
```

is materially different from:

```text
VerificationStatus.UNKNOWN
BackendExecutionStatus.UNKNOWN
```

## Error contract

A backend technical exception raises `BackendExecutionError`. The exception
contains backend-neutral execution evidence whose status is `ERROR`.

Technical errors are not converted into verification reports. They belong to
the runtime error boundary and can be handled by a CLI, CI integration or
orchestrator.

## Total budget

The timeout is a total property budget. It begins before backend translation
and is not reset for internal calls. Optional diagnostics may be skipped if no
budget remains; the primary logical result remains valid and the missing
diagnostic is reported.

## Serialization

Reports store only a policy snapshot:

```json
{
  "status": "timeout",
  "duration_ms": 10002.31,
  "reason": "Verification inconclusive: the backend execution timed out.",
  "backend_reason": "timeout",
  "policy": {
    "timeout_ms": 10000,
    "max_backend_units": null,
    "max_memory_mb": null,
    "deterministic_seed": null,
    "backend_options": {}
  }
}
```

The cancellation token is intentionally absent because it is mutable runtime
state, not provenance.

## Backend adapter checklist

A new adapter is complete only when it has tests proving that it:

- declares execution capabilities;
- maps every supported generic field to native controls;
- rejects unsupported controls;
- normalizes timeout, resource and cancellation reasons;
- measures total duration;
- preserves the policy snapshot;
- raises structured technical errors;
- does not claim support for controls it cannot enforce.
