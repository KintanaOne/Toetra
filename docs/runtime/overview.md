# Runtime Overview

> Status: High-level Z3 runtime implemented  
> Implementation: `dsl.runtime`, backend routing, execution and reporting

## Purpose

The FORML runtime owns the user-facing execution path from a specification and
model artifacts to backend-neutral reports.

```text
.forml file or source
→ model schema construction
→ AST and semantic validation
→ IR1
→ IR2 verification tasks
→ capability routing
→ backend runner
→ VerificationResult
→ VerificationReport
→ text / JSON
```

Low-level compiler functions remain available, but a normal user should start
with:

```python
from dsl.runtime import verify
```

## High-Level API

```python
session = verify(
    "policy.forml",
    model="model.joblib",
    dataset="reference.csv",
)
```

The runtime can also consume an already normalized schema:

```python
session = verify(source, schema=model_schema)
```

Providing both `schema` and model artifacts is rejected because it would make
the source of model metadata ambiguous.

When a `.forml` path is supplied and `model` is omitted, the `model := ...`
reference from the FORML header is resolved relative to the specification file.
The target name defaults to the header target and must match the resulting
`ModelSchema`. This prevents the property and model assumptions from referring
to different outputs.

## Verification Session

`verify(...)` returns a `VerificationSession` containing one
`VerificationExecution` per property.

```python
session.reports
session.results
session.executions
```

The session is also a read-only sequence:

```python
first_execution = session[0]
for execution in session:
    ...
```

Convenience properties support scripts and CI jobs:

| Property | Meaning |
|---|---|
| `is_successful` | Every property ended as `PROVED` or `WITNESS` |
| `has_failures` | A `COUNTEREXAMPLE` or `NO_WITNESS` exists |
| `has_unknown` | At least one backend returned `UNKNOWN` |
| `exit_code` | `0` success, `1` failure, `2` inconclusive |

## Output Helpers

```python
session.print()
text = session.to_text()
json_text = session.to_json()
session.write_json("artifacts/forml-report.json")
```

All output is produced by `dsl.reporting`. The runtime and backend never format
terminal or notebook output themselves.

## Runtime Registries

The high-level runtime uses two separate registries:

```text
BackendRegistry
→ capabilities used by the router

BackendRunnerRegistry
→ concrete executor used after routing
```

The default runtime registers Z3 in both. Advanced integrations can inject
custom registries into `verify(...)` without changing the compiler or reporting
contracts.

## Current V1 Profile

```text
numeric affine properties
+ typed input domains
+ affine model assumptions
→ Z3
→ PROVED / COUNTEREXAMPLE / WITNESS / NO_WITNESS / UNKNOWN
```

## Remaining Runtime Work

- HTML and notebook representation;
- solver timeout and resource options;
- persistent trace identifiers;
- multi-backend execution and comparison;
- richer replay helpers for counterexamples.
