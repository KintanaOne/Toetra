# Runtime overview

> **Status:** Implemented for the public V1 routes
>
> **Public facade:** `toetra`
>
> **Internal ownership:** `toetra._runtime`, routing, reporting, and provenance

The runtime turns one public `verify(...)` request into a completed
`VerificationSession`.

```text
source/path + model/schema + optional anchors/policy
→ resolve inputs
→ compile one IR2 task per property
→ route and execute each task
→ apply compatibility policies
→ build reports and provenance
→ return session
```

## Public entry point

```python
from toetra import verify

session = verify(
    "policy.toetra",
    model="model.joblib",
    dataset="reference.csv",
)
```

The runtime can consume an explicit normalized schema instead of model
artifacts. The two metadata paths are mutually exclusive.

See the complete [public API reference](../api-reference/index.md).

## Per-property execution

For each `VerificationTaskIR2`, the runtime stores one private
`VerificationExecution` containing:

- task;
- selected `BackendRoute`;
- backend-neutral `VerificationResult`;
- public `VerificationReport`.

The session exposes reports and ergonomic findings rather than making those
private compiler/backend objects part of the root API.

## Runtime registries

Two registries have distinct responsibilities:

| Registry | Responsibility |
|---|---|
| `BackendRegistry` | capability profiles used for routing |
| `BackendRunnerRegistry` | concrete executors used after routing |

The default runtime registers Z3 in both. Advanced injection keywords on
`verify(...)` support development and integration testing, but their accepted
types remain private.

## Execution policy

The runtime applies one backend-neutral policy to each property. It covers:

- total timeout;
- backend work/resource limits;
- cooperative cancellation;
- deterministic seed;
- adapter-specific options.

Routing rejects a backend that cannot enforce a requested control. The policy
snapshot and technical termination evidence are retained in reports.

## Reports

```python
session.print()
text = session.to_text()
payload = session.to_json()
paths = session.write_artifacts("artifacts", formats={"json", "html"})
```

All renderers consume backend-neutral reports. JSON uses the frozen
`toetra.verification-report` schema version 6.

## Findings and replay

```python
finding = session.first_counterexample
if finding is not None:
    replay = finding.replay()
    frame = replay.to_dataframe()
```

Replay reconstructs point inputs, invokes the concrete model through a runtime
observer, compares formal and observed outputs, and reevaluates the preserved
original property. It is available only when the session retains the required
model and assignment evidence.

## Status and process exit

The five logical statuses are `PROVED`, `COUNTEREXAMPLE`, `WITNESS`,
`NO_WITNESS`, and `UNKNOWN`.

Session exit semantics are:

| Exit code | Meaning |
|---|---|
| `0` | every property is `PROVED` or `WITNESS` |
| `1` | at least one `COUNTEREXAMPLE` or `NO_WITNESS` |
| `2` | no logical failure, but at least one `UNKNOWN` |

Exceptions before session completion do not produce an exit code or partial
session.

## V1 boundary

The runtime is complete for the routes in the
[public V1 profile](../public-v1-profile.md). Multi-backend comparison, remote
execution, persistent monitoring, and autonomous orchestration remain post-V1
directions rather than missing stages in the current request lifecycle.
