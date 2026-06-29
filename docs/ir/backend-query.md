# Backend Query

> Status: Planned / Critical  
> Implementation: Not implemented yet  
> Scope: Final backend-specific verification artifact

## Purpose

`BackendQuery` is the final artifact produced before FORML calls a verification backend.

It represents the complete verification problem in a format understood by a specific backend.

Examples may include:

- Z3 expressions,
- ERAN-compatible robustness queries,
- future solver-specific artifacts,
- runtime verification plans.

---

## Why BackendQuery Exists

FORML must remain backend-agnostic for as long as possible.

DSL syntax, semantic validation, IR normalization, model constraints, and assertion aggregation should not directly depend on one solver.

`BackendQuery` is the explicit boundary where backend independence ends.

---

## Pipeline Position

```text
.forml
    ↓
SemanticValidatedAST
    ↓
IR1-NNF
    ↓
IR2-CNF/DNF
    ↓
AggregatedAssertionSet
    ↓
LoweredQuery
    ↓
BackendQuery
    ↓
Verification Backend
```

---

## Input Contract

A backend query should be produced from a lowered and minimized representation.

Input should include:

- normalized logical structure,
- model constraints,
- scope constraints,
- backend selection,
- backend capability metadata,
- traceability metadata,
- diagnostics from previous layers.

---

## Output Contract

A `BackendQuery` should include:

| Field | Role |
|---|---|
| backend | Target backend. |
| query | Backend-specific expression or artifact. |
| assumptions | Required assumptions. |
| constraints | Encoded verification constraints. |
| metadata | Traceability and compilation metadata. |
| diagnostics | Warnings or known limitations. |

Conceptual shape:

```text
BackendQuery
├── backend
├── query
├── assumptions
├── constraints
├── metadata
└── diagnostics
```

---

## Backend-Specific Examples

### Z3

A Z3 backend query may contain:

- symbolic variables,
- model equations or approximations,
- property constraints,
- negated property for counterexample search,
- solver configuration.

---

### ERAN

An ERAN-oriented query may contain:

- model representation,
- perturbation bounds,
- robustness property,
- abstract domain selection.

---

### Runtime Backend

A runtime verification backend may contain:

- executable checks,
- monitoring hooks,
- data capture rules,
- result interpretation logic.

---

## Invariants

A valid `BackendQuery` must satisfy:

| Invariant | Description |
|---|---|
| Backend-specific | The artifact is tied to one backend. |
| Fully lowered | No high-level DSL-only construct should remain unresolved. |
| Semantically grounded | Query must trace back to validated semantics. |
| Model-aware | Query must be compatible with model schema and constraints. |
| Executable or serializable | The backend should be able to consume it. |
| Diagnostic-rich | Unsupported constructs should be reported clearly. |

---

## Relationship with Backend Orchestration

Backend orchestration may happen before, during, or after lowering depending on design.

However, `BackendQuery` is always produced after the backend is known.

The orchestration layer determines:

- which backend is selected,
- which strategy is used,
- which capabilities are required,
- which limitations apply.

---

## Relationship with Lowering and Minimization

Lowering prepares the query.

BackendQuery encodes it.

```text
LoweredQuery → BackendQuery
```

Lowering should remain as backend-independent as possible.  
BackendQuery is backend-specific by design.

---

## Relationship with Miova

Miova can test backend query generation by mutating:

- lowered constraints,
- backend capability metadata,
- model constraints,
- property constraints,
- expected unsupported cases.

Expected outcomes include:

- valid backend query,
- unsupported backend diagnostic,
- early rejection,
- contract failure,
- invalid query prevention.

---

## Summary

`BackendQuery` is the final boundary between FORML's internal formal pipeline and external verification engines.

It must be explicit, traceable, diagnostic-rich, and backend-specific.
