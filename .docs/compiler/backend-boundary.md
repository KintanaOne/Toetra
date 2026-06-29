# Backend Boundary

> Status: P0 / Planned / Critical  
> Scope: LoweredQuery to BackendQuery  
> Implementation: Not yet implemented  
> Audience: backend authors, solver integration authors, architecture maintainers

## Purpose

The backend boundary defines where FORML stops being backend-independent and starts producing backend-specific artifacts.

It answers the question:

```text
What exactly is sent to Z3, ERAN, or another verification backend?
```

This boundary is critical because it prevents solver-specific implementation details from leaking into earlier compiler layers.

---

## Position in the Pipeline

```text
LoweredQuery
    ↓
Backend Boundary
    ↓
BackendQuery
    ↓
Verification Backend
```

---

## Boundary Principle

Before the backend boundary, FORML artifacts are backend-independent or backend-preparable.

After the backend boundary, artifacts may be backend-specific.

| Before Boundary | After Boundary |
|---|---|
| `VerificationTask` | Backend-specific query |
| `IR1` | Z3 expression, ERAN config, etc. |
| `IR2` | Backend-specific clauses or constraints |
| `AggregatedAssertionSet` | Solver-level assertion set |
| `LoweredQuery` | Executable backend artifact |

---

## Inputs

The backend boundary should consume:

```text
LoweredQuery
```

It may also require:

- backend selection result;
- backend capability metadata;
- model encoding strategy;
- ModelBridge-derived model constraints;
- diagnostics context;
- execution options.

---

## Output

The backend boundary produces:

```text
BackendQuery
```

A `BackendQuery` is backend-specific.

Examples:

| Backend | Possible BackendQuery |
|---|---|
| Z3 | SMT expressions, solver assertions, variables, constraints. |
| ERAN | Abstract domain config and property specification. |
| Future ONNX checker | Model + property validation artifact. |
| Runtime monitor | Runtime predicate or monitor configuration. |

---

## BackendQuery Contract

A `BackendQuery` should contain:

- backend identifier;
- encoded assertions;
- encoded model constraints;
- execution parameters;
- traceability metadata;
- source property references;
- expected result type;
- diagnostics hooks.

---

## Backend Capability Checks

The backend boundary must validate that the selected backend can handle the query.

Examples:

- supported property type;
- supported model framework;
- supported logical operators;
- supported normal form;
- supported metric;
- supported perturbation domain;
- supported numeric types;
- supported output type.

Unsupported requests should fail early with diagnostics.

---

## Z3 Boundary Example

For a future Z3 backend, the backend boundary may transform:

```text
LoweredQuery
```

into:

```text
Z3 variables
Z3 constraints
Z3 solver assertions
Z3 check command
```

The Z3 backend should not need to know how `.forml` syntax was parsed. It should receive a lowered, explicit, backend-ready problem.

---

## What Must Not Cross Backwards

Backend-specific objects must not cross backward into earlier layers.

Examples of forbidden leakage:

| Forbidden | Reason |
|---|---|
| Z3 objects inside AST | AST must remain backend-independent. |
| Solver expressions inside semantic annotations | Semantic layer should not depend on backend libraries. |
| ERAN-specific concepts inside IR1 | IR1 must remain backend-independent. |
| Backend compiler assumptions inside parser | Parser should only know syntax. |

---

## Guarantees

The backend boundary must guarantee:

- backend-specific objects are created only here or later;
- unsupported queries fail with diagnostics;
- backend capabilities are checked explicitly;
- traceability is preserved into backend artifacts;
- backend execution is separated from backend query construction;
- backend results can be mapped back to FORML properties.

---

## Relation to Runtime

The backend boundary creates the query.

The runtime executes the query.

These should remain separate responsibilities:

```text
Backend Boundary = compile query
Verification Runtime = execute query
```

---

## Relation to Miova

Miova can challenge the backend boundary by mutating:

- lowered queries;
- backend capabilities;
- backend hints;
- model constraints;
- normal form metadata;
- expected result types.

Expected outcomes include:

- unsupported query rejection;
- stable diagnostics;
- no solver crash from invalid preconditions;
- traceability preservation.
