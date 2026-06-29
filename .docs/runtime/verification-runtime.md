# Verification Runtime

> Status: Planned  
> Implementation: Not yet implemented  
> Scope: Execution of backend-ready verification artifacts

## Purpose

The verification runtime is the execution layer that receives a `BackendQuery`, invokes a verification backend, and returns a normalized `VerificationResult`.

It is the final stage of the first functional FORML end-to-end path.

## Runtime Position

```text
LoweredQuery
→ BackendQuery
→ VerificationRuntime
→ VerificationResult
```

The runtime should not be coupled to the DSL syntax, AST structure, or semantic validation internals.

## Minimal V1 Execution Path

The minimal V1 execution path is Z3-based:

```text
BackendQuery[Z3]
→ Z3RuntimeAdapter
→ z3.Solver()
→ native Z3 result
→ VerificationResult
```

Z3 is the reference backend for V1.

Other backends must not be required for the first complete FORML execution.

## Runtime Inputs

The runtime consumes backend-specific artifacts.

### BackendQuery

A `BackendQuery` represents the final backend-specific form of a FORML verification problem.

It should contain:

- backend identifier,
- symbolic variables,
- assertions,
- solver configuration,
- traceability metadata,
- optional model constraints,
- optional expected property metadata.

### Runtime Options

Runtime options may include:

- timeout,
- solver mode,
- determinism settings,
- diagnostic level,
- counterexample extraction,
- trace verbosity.

For V1, runtime options should remain minimal.

## Runtime Output

The runtime should produce a normalized `VerificationResult`.

Possible fields:

```text
VerificationResult
    status
    property_id
    backend
    satisfied
    counterexample
    diagnostics
    raw_backend_summary
    trace
```

## Suggested Result Statuses

| Status | Meaning |
|---|---|
| `SATISFIED` | The property was verified or no counterexample was found under the backend semantics |
| `VIOLATED` | A counterexample or violation was found |
| `UNKNOWN` | The backend could not determine the result |
| `TIMEOUT` | Execution exceeded limits |
| `UNSUPPORTED` | The query requires unsupported backend features |
| `ERROR` | Runtime or backend execution failed unexpectedly |

## Z3 Runtime Adapter

The Z3 adapter should be responsible for:

- constructing a `z3.Solver`,
- declaring symbolic variables,
- adding assertions,
- executing solver checks,
- extracting models/counterexamples,
- mapping native Z3 statuses to FORML statuses,
- returning a normalized `VerificationResult`.

## Adapter Boundary

The runtime should expose a clear adapter boundary:

```python
class VerificationBackendAdapter:
    def execute(self, query: BackendQuery, options: RuntimeOptions) -> VerificationResult:
        ...
```

For V1, one concrete implementation is enough:

```python
class Z3BackendAdapter(VerificationBackendAdapter):
    ...
```

## Error Handling

Runtime errors must preserve the layer where the error occurred.

Examples:

| Error | Layer |
|---|---|
| malformed `BackendQuery` | backend-boundary |
| unsupported symbolic operator | backend-adapter |
| solver timeout | runtime |
| native backend crash | backend-runtime |
| inconsistent result mapping | result-normalization |

Runtime errors should not be reclassified as parser or semantic errors.

## Traceability

A runtime result should be traceable back to:

- the FORML property,
- the generated IR task,
- the aggregated assertion set,
- the lowered query,
- the backend query,
- the backend execution result.

This traceability is critical for diagnostics, debugging, and future Miova campaigns.

## V1 Constraints

For V1, the verification runtime should intentionally avoid:

- automatic backend selection,
- runtime monitoring,
- distributed execution,
- multi-backend comparison,
- complex optimization at runtime.

Those concerns belong to post-V1 work.

## Target V1 Definition of Done

A minimal runtime is acceptable when:

- a valid FORML property reaches a Z3 `BackendQuery`,
- the Z3 adapter executes it,
- a normalized `VerificationResult` is returned,
- failures are layer-specific,
- at least one counterexample path is supported,
- the flow is covered by golden end-to-end tests.
