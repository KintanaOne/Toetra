# Verification Task

> Status: Implemented / Stabilizing  
> Implementation: IR1 root execution unit  
> Scope: Property-level verification representation

## Purpose

`VerificationTask` is the top-level IR1 unit produced by the FORML compiler after semantic validation.

A verification task represents one property that must be checked against a model, backend, or verification strategy.

It is the first structured artifact where the user property is detached from DSL syntax and represented as a backend-independent logical task.

---

## Conceptual Shape

```text
VerificationTask
├── property_type
├── scope
├── query
└── backend
```

Each task contains:

| Field | Role |
|---|---|
| `property_type` | The FORML property category, such as ROBUSTNESS, FAIRNESS, MONOTONICITY, BOUND, LOGIC. |
| `scope` | The semantic context where the property is evaluated. |
| `query` | The logical expression or problem-level predicate to verify. |
| `backend` | Optional backend hint explicitly requested by the user. |

---

## Why VerificationTask Exists

The DSL is user-oriented. The backend is solver-oriented.

`VerificationTask` is the first compiler artifact that starts bridging the two.

It answers:

```text
For this property, under this semantic scope, what logical query must be verified?
```

---

## Input

`VerificationTask` is produced from a semantically validated property.

The input must already satisfy:

- valid property structure,
- valid LHS scope,
- resolved bindings,
- valid logical expression,
- property/scope compatibility,
- optional backend syntax correctness.

---

## Output

The output is a backend-independent task that can be consumed by later IR passes.

It is not yet a backend query.

It should not contain:

- CST nodes,
- raw Lark nodes,
- unresolved AST references,
- backend-specific solver objects,
- serialized model internals.

---

## Invariants

A valid `VerificationTask` must satisfy:

| Invariant | Description |
|---|---|
| Property is normalized | The property type must be represented by the official vocabulary enum. |
| Scope is explicit | The task must contain a `ScopeIR`; implicit DSL scope must not leak further. |
| Query is structured | The RHS assertion must be represented as `QueryIR`. |
| Backend is optional | A task can remain backend-agnostic until orchestration. |
| No syntax leakage | CST and source syntax must not appear in the task. |
| Semantic resolution is preserved | Entity and feature references should use semantic resolution results. |

---

## Current Limitations

The current implementation is a strong IR1 foundation, but several details must be stabilized:

- backend enum normalization must be robust to casing and enum/value differences;
- pairwise variable splitting must align with the semantic validator convention;
- comparison translation should consume semantic annotations rather than raw parsed entities;
- problem/function enum conversion should be normalized consistently;
- IR1 should explicitly distinguish current raw logical structure from normalized NNF form.

These limitations are implementation details, not architectural flaws. They are exactly the kind of boundary issues that contract tests and Miova campaigns should expose.

---

## Relationship with IR1

`VerificationTask` is the root object of IR1.

IR1 should eventually guarantee that the logical query is in the expected IR1 normal form, including implication elimination and NNF where applicable.

---

## Relationship with IR2

IR2 consumes one or more `VerificationTask` objects and prepares them for a specific logical strategy.

Examples:

```text
VerificationTask.query
    → IR2 CNF form
```

or:

```text
VerificationTask.query
    → IR2 DNF form
```

depending on backend needs or exploration strategy.

---

## Relationship with ModelBridge

`VerificationTask` alone does not encode the model.

The model enters the verification pipeline through `ModelSchema` and future model-derived constraints.

The later aggregation layer combines:

```text
VerificationTask + ModelSchema-derived constraints → AggregatedAssertionSet
```

---

## Relationship with Miova

`VerificationTask` is a strong mutation target.

Miova can challenge:

- property type consistency,
- scope/query compatibility,
- backend selection,
- invalid logical structures,
- mutation of comparison operators,
- mutation of scope variables,
- invalid or missing query leaves.

Expected outcomes should be defined by the IR contract.

---

## Summary

`VerificationTask` is the first formal execution unit of FORML.

It is not the final solver query. It is the canonical task object that carries property intent from the semantic compiler into the logical verification pipeline.
