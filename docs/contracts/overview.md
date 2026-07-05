# Contracts Overview

> Status: P0 / Architecture Baseline  
> Scope: FORML artifact boundaries and verification contracts  
> Implementation: Mixed — implemented, stabilizing and planned contracts  
> Audience: FORML maintainers, contributors, Miova campaign authors, backend implementers

## Purpose

FORML is organized as a sequence of explicit artifact transformations.

A contract defines the boundary between two layers.

It answers the question:

```text
What must be true before and after a transformation?
```

Contracts make FORML testable, evolvable and mutation-resilient.

They prevent the system from becoming a loose sequence of ad-hoc conversions.

---

## Contracted Pipeline

The target FORML end-to-end pipeline is:

```text
.forml source
    ↓
Source → CST
    ↓
CST → AST
    ↓
AST → SemanticValidatedAST
    ↓
SemanticValidatedAST → IR1 / NNF
    ↓
IR1 → IR2 / CNF-DNF
    ↓
IR2 + Model Constraints → AggregatedAssertionSet
    ↓
AggregatedAssertionSet → LoweredQuery
    ↓
LoweredQuery → BackendQuery
```

The ModelBridge pipeline contributes a second source of truth:

```text
model artifact
    ↓
Model → ModelSchema
    ↓
ModelSchema → semantic validation support
    ↓
ModelSchema → model constraints
```

---

## Contract Categories

| Category | Documents | Purpose |
|---|---|---|
| Compiler contracts | source, CST, AST, semantic, IR | Stabilize the DSL compiler pipeline. |
| Logical contracts | IR1, IR2, aggregation, lowering | Stabilize logical normalization and verification preparation. |
| ModelBridge contracts | model schema, semantic integration, model constraints | Connect ML artifacts to FORML verification. |
| Backend contracts | IR to backend, backend query | Define solver-facing boundaries. |
| Cross-cutting contracts | errors, type normalization, mutation boundaries | Stabilize failure semantics and testing strategy. |

---

## Contract Template

Each contract should define:

| Section | Meaning |
|---|---|
| Purpose | Why this boundary exists. |
| Input | Accepted artifact and preconditions. |
| Output | Produced artifact and required invariants. |
| Guarantees | What downstream layers may rely on. |
| Non-goals | What this layer must not do. |
| Failure modes | Expected errors and rejection cases. |
| Miova hooks | Where mutations may challenge the boundary. |

---

## Current vs Target Guarantees

FORML contracts intentionally distinguish:

| Label | Meaning |
|---|---|
| Implemented | Present in the current codebase. |
| Stabilizing | Present but requiring cleanup, normalization, or stricter test. |
| Planned / Critical | Not implemented yet, but required for end-to-end verification. |
| Research Direction | Future exploration beyond the first stable end-to-end path. |

This lets the documentation describe the target architecture without pretending every layer already exists.

---

## Relationship with Miova

Miova is not part of the normal FORML verification path.

Miova is used to challenge FORML's contracts.

It can mutate artifacts such as:

- source strings;
- CST-like structures;
- AST nodes;
- semantic annotations;
- IR1 logical expressions;
- planned IR2 forms;
- ModelSchema objects;
- aggregated assertions;
- backend-preparable queries.

A contract is considered stronger when it can survive controlled mutations and reject invalid artifacts at the correct boundary.
