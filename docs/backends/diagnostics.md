# Backend Diagnostics

> Status: Planned / critical for usability  
> Scope: Backend errors, incompatibility explanations, verification results  
> Priority: P1

## Purpose

Backend diagnostics explain what happened during backend selection, query generation, execution, or result interpretation.

They are essential because verification failures can come from very different causes:

- invalid user property;
- unsupported model type;
- unsupported backend capability;
- impossible encoding;
- solver timeout;
- inconclusive backend result;
- real property violation.

FORML should distinguish these cases clearly.

## Diagnostic philosophy

FORML diagnostics should be:

| Principle | Meaning |
|---|---|
| Layer-aware | The diagnostic identifies where the problem occurred. |
| Contract-aware | The violated precondition or invariant is named when possible. |
| User-readable | The message explains what the user can change. |
| Machine-readable | Diagnostics can be tested and processed. |
| Non-silent | FORML should not silently fallback to another backend without reporting it. |

## Backend diagnostic categories

| Category | Meaning |
|---|---|
| Backend not found | Requested backend is unknown or not registered. |
| Backend incompatible | Backend exists but cannot support the request. |
| Capability mismatch | Property/model/query exceeds backend capability. |
| Encoding failure | FORML cannot compile the lowered query to backend-native form. |
| Execution failure | Backend crashed, timed out, or failed externally. |
| Inconclusive result | Backend returned unknown or could not decide. |
| Property violation | Backend found a counterexample or failing condition. |
| Property verified | Backend confirmed the property under assumptions. |

## Suggested diagnostic model

A future diagnostic structure may look like:

```python
@dataclass(frozen=True)
class BackendDiagnostic:
    layer: str
    backend: str | None
    code: str
    severity: str
    message: str
    details: dict[str, Any]
    suggested_fix: str | None = None
```

This keeps diagnostics testable and suitable for CLI, CI, reports, and IDE extensions.

## Suggested diagnostic codes

```text
BACKEND_NOT_FOUND
BACKEND_UNSUPPORTED_PROPERTY
BACKEND_UNSUPPORTED_MODEL
BACKEND_UNSUPPORTED_LOGICAL_FORM
BACKEND_UNSUPPORTED_CONSTRAINT
BACKEND_ENCODING_FAILED
BACKEND_EXECUTION_FAILED
BACKEND_TIMEOUT
BACKEND_UNKNOWN_RESULT
BACKEND_COUNTEREXAMPLE_FOUND
BACKEND_PROPERTY_VERIFIED
```

## Examples

### Unknown backend

```text
BACKEND_NOT_FOUND
Backend 'foo' is not registered. Available backends: z3, ERAN, box, zonotope.
```

### Unsupported property

```text
BACKEND_UNSUPPORTED_PROPERTY
Backend 'z3' does not currently support property 'ROBUSTNESS' for model type 'XGBClassifier'.
```

### Unsupported logical form

```text
BACKEND_UNSUPPORTED_LOGICAL_FORM
Backend 'eran' cannot consume DNF queries with nested disjunctions. Try a supported robustness-only assertion form.
```

### Encoding failure

```text
BACKEND_ENCODING_FAILED
Could not encode feature 'age' because its dtype is missing from ModelSchema.
```

### Inconclusive result

```text
BACKEND_UNKNOWN_RESULT
Backend 'z3' returned UNKNOWN. The property was not proved or refuted.
```

## Difference between invalid, unsupported, and violated

These cases must not be confused.

| Case | Meaning |
|---|---|
| Invalid | The FORML specification breaks language or semantic rules. |
| Unsupported | The specification is valid, but the backend cannot handle it. |
| Violated | The backend successfully checked the property and found a counterexample. |
| Inconclusive | The backend ran but could not decide. |

This distinction is critical for CI/CD workflows.

## Relationship with contracts

Backend diagnostics are connected to several contract documents:

| Contract | Diagnostic role |
|---|---|
| `errors.md` | Global error taxonomy. |
| `ir-to-backend.md` | Backend query preconditions. |
| `type-normalization.md` | Normalized enum/type failures. |
| `mutation-boundaries.md` | Expected mutated failures. |
| `model-constraints.md` | Missing or unsupported model constraints. |

## CI behavior

In CI, FORML should distinguish between:

| Result | CI meaning |
|---|---|
| verified | pass |
| violated | fail |
| invalid specification | fail fast |
| unsupported backend | fail or skip depending on configuration |
| inconclusive | configurable, often fail in strict mode |
| timeout | configurable, usually fail in strict mode |

## Miova and diagnostics

Miova campaigns should assert not only whether a mutation fails, but how it fails.

For example:

```text
Mutation: replace backend z3 with unknown backend foo
Expected: BACKEND_NOT_FOUND
```

```text
Mutation: remove dtype from ModelSchema feature
Expected: BACKEND_ENCODING_FAILED or MODEL_SCHEMA_INVALID
```

This makes diagnostics part of the contract, not just user-facing text.

## Design invariant

A backend failure without a diagnostic is itself a FORML failure.

