# Backends Syntax

> Status: Implemented / target boundary planned  
> Scope: User-facing backend syntax  
> Priority: P1  
> Audience: FORML users, backend contributors, compiler maintainers

## Purpose

FORML allows properties to optionally specify a backend.

The backend syntax is part of the language surface, but backend execution is not handled directly by the language layer.

The DSL may express:

```forml
using z3
```

but the backend boundary later decides whether the query can actually be lowered and executed by that backend.

---

## Basic Syntax

Backend syntax appears after a property:

```forml
[BOUND]: check_at x => score >= 0 using z3
```

With arguments:

```forml
[ROBUSTNESS]: at x in neighborhood(metric=L2, eps=0.1) => CLASSIFICATION.EQUAL() using z3(timeout=30)
```

---

## Supported Backend Names

Current grammar-level backend names include:

| Backend Syntax | Intended Backend / Mode | Status |
|---|---|---|
| `z3` / `Z3` | SMT backend | planned critical backend |
| `eran` / `ERAN` | Neural network verification backend | planned |
| `zonotope` / `ZONOTOPE` | Abstract domain / backend mode | planned |
| `box` / `BOX` | Abstract domain / backend mode | planned |

Backend names should be normalized internally.

Recommended canonical enum names:

```text
Z3
ERAN
ZONOTOPE
BOX
```

---

## Backend Arguments

Backends may accept optional arguments:

```forml
using z3(timeout=30)
using eran(domain="zonotope")
```

Arguments are parsed as key/value pairs.

The language layer should not validate backend-specific semantics deeply. It should preserve arguments for backend capability validation.

---

## Backend Hint vs Backend Selection

A backend declaration can be interpreted in two possible ways:

| Interpretation | Meaning |
|---|---|
| Backend hint | User suggests a preferred backend, but FORML may select another compatible backend. |
| Backend selection | User requires this backend; incompatible requests fail. |

Recommended target behavior:

```text
Explicit backend declarations are treated as required unless a future configuration allows fallback.
```

This should be clarified in backend orchestration documentation.

---

## Backend Boundary

The backend syntax does not mean the property is immediately executable.

The full path is:

```text
DSL backend declaration
→ AST BackendNode
→ semantic/backend compatibility check
→ IR backend field
→ backend capability matching
→ backend query lowering
→ execution
```

A backend may reject a property because:

- the property type is unsupported,
- the model framework is unsupported,
- the logical form is unsupported,
- the required ModelBridge constraints are unavailable,
- the backend cannot handle the scope type,
- the backend does not support the requested metric or domain.

---

## Backend and ModelBridge

ModelBridge does not replace the backend.

ModelBridge provides normalized information about the model:

```text
model artifact
→ loaded model
→ framework detection
→ model introspection
→ ModelSchema
```

The backend consumes logical and model-aware constraints after aggregation and lowering.

Conceptually:

```text
IR2
+ Model Constraints
→ AggregatedAssertionSet
→ LoweredQuery
→ BackendQuery
```

---

## Backend and IR2

Backend selection may depend on the normal form required.

Examples:

| Backend Need | Possible IR2 Form |
|---|---|
| SAT/SMT-style solving | CNF-like structure |
| scenario exploration | DNF-like structure |
| abstract interpretation | backend-specific abstract constraints |
| counterexample search | minimized query or case split |

The backend syntax therefore does not fully determine the lowering strategy. It only participates in backend orchestration.

---

## Error Cases

### Unknown backend

```forml
[BOUND]: check_at x => score >= 0 using unknown_backend
```

Expected result:

```text
Parser or builder rejects the backend if not in grammar.
```

### Unsupported backend-property pair

```forml
[FAIRNESS]: x ~ x' in neighborhood(metric=L2, eps=0.1) => CLASSIFICATION.EQUITY() using box
```

Expected result:

```text
Backend capability validation rejects the request if unsupported.
```

### Unsupported backend argument

```forml
[BOUND]: check_at x => score >= 0 using z3(non_existing_option=true)
```

Expected result:

```text
Backend argument validation rejects or warns, depending on the backend policy.
```

---

## Testing Requirements

Backend syntax tests should include:

- backend without arguments,
- backend with one argument,
- backend with multiple arguments,
- lowercase and uppercase names,
- unsupported backend names,
- malformed backend calls,
- backend compatibility tests,
- backend argument validation tests,
- Miova mutations of backend names and arguments,
- Hypothesis generation of backend configurations.

---

## Related Documents

- [Backends Overview](../backends/overview.md)
- [Backend Capabilities](../backends/capabilities.md)
- [Backend Orchestration](../backends/orchestration.md)
- [Backend Boundary](../compiler/backend-boundary.md)
- [IR to Backend Contract](../contracts/ir-to-backend.md)
