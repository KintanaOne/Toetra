# Results and Traces

> Status: Planned  
> Implementation: Not yet implemented  
> Scope: Normalized verification outputs and traceability metadata

## Purpose

FORML should return structured verification results rather than raw backend outputs.

The result layer normalizes backend-specific responses and preserves enough traceability to explain how a result was produced.

## Result Position

```text
BackendQuery
→ VerificationRuntime
→ BackendRawResult
→ VerificationResult
→ DiagnosticTrace
```

## VerificationResult

A `VerificationResult` is the normalized output of a verification run.

Suggested shape:

```text
VerificationResult
    property_id
    status
    satisfied
    backend
    counterexample
    diagnostics
    trace
    raw_backend_summary
```

## Status Semantics

| Status | Meaning |
|---|---|
| `SATISFIED` | The property is verified according to the backend semantics |
| `VIOLATED` | The backend found a violation or counterexample |
| `UNKNOWN` | The backend could not prove or disprove the property |
| `TIMEOUT` | The backend exceeded execution limits |
| `UNSUPPORTED` | The query requires unsupported backend features |
| `ERROR` | An unexpected backend/runtime error occurred |

## Counterexamples

When a backend finds a violation, FORML should preserve the counterexample in a normalized form.

A counterexample may include:

- feature assignments,
- symbolic variable values,
- violated assertion identifiers,
- model-side constraints involved,
- source property reference.

For V1, counterexample extraction should focus on Z3.

## DiagnosticTrace

A diagnostic trace explains how the result was obtained.

It should preserve references to:

```text
SourceProperty
CST node
AST node
SemanticValidatedAST node
IR1 task
IR2 form
AggregatedAssertionSet
LoweredQuery
BackendQuery
BackendRawResult
```

The goal is not to expose every internal object to the user.

The goal is to preserve enough traceability for debugging, testing, and future reporting.

## Trace Granularity

FORML may support several trace levels:

| Level | Description |
|---|---|
| `none` | Only return result status |
| `summary` | Return property, backend, status, and high-level diagnostics |
| `debug` | Include compiler and lowering trace references |
| `full` | Include all available trace metadata |

V1 can start with `summary` and `debug`.

## Relationship With Golden Tests

Golden samples should assert not only that a result exists, but also that traceability is preserved.

Example checks:

```text
- property id is preserved
- backend is Z3
- status is normalized
- diagnostics mention unsupported constructs when relevant
- counterexample exists when expected
```

## Relationship With Miova

Miova can test result and trace robustness by mutating:

- backend raw outputs,
- diagnostic payloads,
- result statuses,
- trace references,
- counterexample structures.

Expected failures should be explicit.

## Result Boundary Invariants

A valid `VerificationResult` must:

- identify the backend,
- expose a normalized status,
- preserve property traceability,
- avoid leaking backend-specific exceptions directly,
- distinguish unknown from failure,
- distinguish violation from runtime error.

## V1 Result Scope

For V1, result handling should prioritize:

```text
Z3 status mapping
counterexample extraction when available
normalized error handling
basic traceability
golden result samples
```

More advanced reporting can come later.
