# Verification Runtime

> Status: Implemented for the numerical-affine Z3 profile  
> Public API: `forml.verify`

## User Entry Point

```python
from forml import verify

session = verify(
    "credit-risk.forml",
    model="credit-risk.joblib",
    dataset="credit-risk-reference.csv",
)
```

The runtime performs the complete orchestration:

```text
load specification
→ resolve or build ModelSchema
→ compile to IR2
→ route each property
→ execute its backend runner
→ build VerificationReport objects
→ return VerificationSession
```

A caller does not need to instantiate `IR2BuildContext`, `BackendRouter` or
`Z3Runner` for the standard path.

## Inputs

### Specification

`specification` accepts either:

- a `Path` to a `.forml` file;
- a string path ending in `.forml`;
- raw FORML source text.

A missing string ending in `.forml` raises `FileNotFoundError` rather than being
misinterpreted as source code.

### Model metadata

Two modes are supported.

Artifact mode:

```python
verify(
    "policy.forml",
    model="model.joblib",
    dataset="reference.csv",
)
```

Schema mode:

```python
verify(source, schema=model_schema)
```

In artifact mode, `ModelManager` loads and introspects the serialized model.
The dataset is optional but may be required to recover input and target dtypes.
If the model path is omitted, the header model reference is resolved relative
to the `.forml` file.

The header target and schema target must match exactly.

## Execution Model

For every compiled property, the runtime creates:

```python
VerificationExecution(
    task=task,
    route=route,
    result=result,
    report=report,
)
```

The task and route remain available for advanced inspection through the
internal runtime layer. Normal application code should consume the session, its
`VerificationFinding` helpers and the report renderers exported by `forml`.


## User Findings and Replay

The session groups results by meaning:

```python
session.proved
session.counterexamples
session.witnesses
session.no_witnesses
session.unknown
```

The first common findings are available directly:

```python
finding = session.first_counterexample
replay = finding.replay() if finding is not None else None
```

`VerificationFinding` exposes normalized `input_values`,
`qualified_input_values` and `output_values`. A replay compares the backend
assignment with the original estimator loaded from the serialized artifact.

## Summary Tables and Artifacts

```python
session.to_records()
session.to_dataframe()
session.write_artifacts("artifacts/", formats={"json", "html"})
```

The neutral records API avoids imposing pandas on lower reporting layers, while
`to_dataframe()` is a convenience for notebook users.

## Runner Registry

Capability registration and execution registration are intentionally separate.
A backend may be known to the router but unavailable in the current process.
In that case the runtime raises `BackendRunnerNotRegisteredError` instead of
silently selecting another executor.

```python
from dsl.runtime import BackendRunnerRegistry

runners = BackendRunnerRegistry()
runners.register(...)
verify(source, schema=schema, runner_registry=runners)
```

## CI Usage

```python
session = verify(...)
session.print()
session.write_json("artifacts/forml-report.json")
raise SystemExit(session.exit_code)
```

Exit codes are stable:

| Code | Meaning |
|---|---|
| `0` | Every property was positively concluded |
| `1` | A property failed |
| `2` | At least one result is inconclusive |

## Error Boundaries

The runtime preserves the original compiler and backend errors. It adds
configuration-specific errors only for ambiguous or disconnected inputs, such
as:

- supplying both a schema and model artifacts;
- a header target that differs from the model schema target;
- a routed backend without a registered runner;
- missing specification, model or dataset files.

## Current Constraints

The public runtime currently executes the default Z3 numerical-affine profile.
It does not yet provide:

- timeouts;
- parallel property execution;
- multi-backend comparison;
- persistent execution traces;
- replay for estimators without a conventional `predict(...)` interface.
