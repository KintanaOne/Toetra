# Lowering and Minimization

> Status: P0 / Planned / Critical  
> Scope: AggregatedAssertionSet to backend-preparable query  
> Implementation: Not yet implemented  
> Audience: backend authors, solver integration authors, optimization authors

## Purpose

The lowering and minimization layer prepares an aggregated verification problem for backend-specific compilation.

It answers the question:

```text
How can the complete verification problem be simplified and shaped before backend encoding?
```

This layer is where FORML can reduce logical complexity, remove redundancies, and prepare solver-friendly expressions.

---

## Position in the Pipeline

```text
AggregatedAssertionSet
    ↓
Lowering / Minimization
    ↓
LoweredQuery
    ↓
Backend Boundary
```

---

## Why This Layer Exists

Backend solvers and verification engines can be expensive.

The compiler should avoid sending unnecessary or poorly shaped constraints when a simpler equivalent or equisatisfiable problem exists.

Lowering and minimization help with:

- performance;
- solver reliability;
- query readability;
- diagnostics;
- counterexample clarity;
- backend compatibility.

---

## Responsibilities

The layer is responsible for:

- simplifying logical expressions;
- removing redundant constraints;
- normalizing backend-preparable structures;
- minimizing assertion sets where safe;
- preserving traceability;
- recording transformations;
- preparing backend-specific compilers without producing backend objects directly.

---

## Possible Transformations

| Transformation | Purpose |
|---|---|
| Constant folding | Remove trivial true/false expressions. |
| Redundancy elimination | Remove duplicated predicates. |
| Constraint subsumption | Remove constraints implied by stronger constraints. |
| Dead branch removal | Remove impossible DNF cases. |
| Clause simplification | Simplify CNF clauses. |
| Domain pruning | Reduce impossible domain branches. |
| Backend compatibility rewrite | Rewrite unsupported patterns into supported equivalents when safe. |

---

## Preservation Modes

Every transformation must state its preservation mode.

| Mode | Meaning |
|---|---|
| Equivalent | Same logical meaning. |
| Equisatisfiable | Same satisfiability result, but not identical meaning. |
| Approximate | Deliberate approximation, must be explicit. |
| Diagnostic-only | No transformation, only metadata. |

For P0, approximate transformations should be avoided unless explicitly flagged.

---

## Output Artifact

The output should be an explicit artifact:

```text
LoweredQuery
```

A `LoweredQuery` may contain:

- simplified logical body;
- preserved scope constraints;
- model constraints;
- backend hint;
- selected normal form;
- transformation trace;
- removed constraints log;
- preservation mode;
- diagnostics.

---

## Minimization Strategy

Minimization should be conservative by default.

The first implementation should favor:

- correctness over aggressiveness;
- traceability over compactness;
- explicit diagnostics over silent rewrites;
- deterministic transformations;
- easy golden testing.

---

## Backend Awareness

This layer may be backend-aware but should remain backend-object-free.

That means it can know that a backend prefers a structure, but it should not instantiate solver terms.

Example:

```text
Allowed:
    Rewrite query into a Z3-friendly conjunction structure.

Not allowed:
    Create z3.BoolRef objects.
```

Backend object creation belongs to backend compilers.

---

## Guarantees

Lowering and minimization must guarantee:

- no required constraint is silently removed;
- every transformation is traceable;
- preservation mode is explicit;
- backend-specific objects are not produced yet;
- invalid simplifications are rejected;
- diagnostics remain meaningful after simplification.

---

## Relation to Backend Boundary

The backend boundary receives a `LoweredQuery` and turns it into a backend-specific artifact.

Therefore:

```text
LoweredQuery = backend-preparable
BackendQuery = backend-specific
```

---

## Relation to Miova

Miova can mutate lowering inputs and outputs to test:

- preservation metadata;
- redundant constraints;
- impossible branches;
- malformed transformation traces;
- missing constraints;
- backend-incompatible rewrites.

Expected checks include:

- no silent semantic drift;
- no orphaned traceability links;
- no invalid minimization accepted;
- no backend object leakage before the backend boundary.
