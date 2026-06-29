# Semantic to IR1 Contract

> Status: P0 / Structural IR1 implemented / NNF planned  
> Scope: SemanticValidatedAST to IR1 / VerificationTask  
> Implementation: IR1 translator exists; NNF/De Morgan are target subphase contracts  
> Audience: IR authors, backend authors, semantic maintainers

## Purpose

The Semantic to IR1 contract defines how validated FORML properties become backend-independent logical verification tasks.

It answers the question:

```text
What is the first formal logical representation of this property?
```

IR1 is not a backend query. It is the first backend-independent logical representation after semantic validation; full NNF normalization is a target subphase, not an implicit guarantee of structural translation.

---

## Input

```text
SemanticValidatedAST
```

The input must provide:

- property type;
- semantic scope;
- resolved variable bindings;
- logical assertion root;
- optional backend hint;
- domain and neighborhood metadata.

---

## Output

```text
list[VerificationTask]
```

Each property becomes one `VerificationTask`.

A task contains:

- `property_type`;
- `scope: ScopeIR`;
- `query: QueryIR`;
- `backend: EnumBackend | None`.

---

## IR1 Artifacts

| Artifact | Meaning |
|---|---|
| `VerificationTask` | Top-level verification unit. |
| `ScopeIR` | Scope extracted from semantic context. |
| `NeighborhoodIR` | Local perturbation information. |
| `DomainIR` | Domain restriction. |
| `QueryIR` | RHS expression wrapper. |
| `LogicalIR` | Backend-independent boolean tree. |
| `ComparisonIR` | Atomic feature predicate. |
| `ProblemIR` | ML problem-level predicate. |

---

## IR1 Logical Responsibilities

IR1 should be responsible for:

- translating semantic AST nodes to logical IR nodes;
- preserving semantic bindings;
- representing scope explicitly;
- representing domain and neighborhood constraints;
- preserving implication explicitly or marking it for normalization;
- defining where De Morgan transformations must occur;
- producing or preserving Negation Normal Form only after the NNF subphase has run.

---

## NNF Invariant

The target IR1-NNF invariant is:

```text
Negations may only appear directly above atomic predicates.
```

Allowed:

```text
NOT ComparisonIR(...)
NOT ProblemIR(...)
```

Not allowed after full NNF normalization:

```text
NOT AndIR(...)
NOT OrIR(...)
NOT ImplyIR(...)
```

---

## Guarantees

If structural IR1 translation succeeds:

- no raw AST logical nodes remain in IR1;
- IR1 references resolved semantic entities, not ambiguous raw attributes;
- backend hints are normalized if present;
- logical structure is backend-independent;
- IR2 may consume the task without re-reading the AST.

---

## Non-Goals

IR1 must not:

- choose CNF or DNF;
- aggregate model constraints;
- minimize the full assertion set;
- encode a solver-specific query;
- execute verification.

---

## Stabilization Notes

The semantic-to-IR1 contract should stabilize:

- use of semantic `resolved_entity` rather than raw attribute entity;
- backend enum normalization;
- pairwise variable splitting;
- quantifier variable representation;
- operator preservation in pretty printing;
- robust handling of `ProblemNode` enums.

---

## Miova Hooks

Miova may mutate semantic or IR1 artifacts by:

- deleting semantic resolution metadata;
- inserting ambiguous attributes;
- replacing logical operators;
- corrupting backend hints;
- injecting non-NNF negation shapes;
- replacing scope metadata.

Expected outcomes:

| Mutation | Expected Boundary |
|---|---|
| Missing semantic binding | Semantic → IR1 rejection. |
| Valid alternative logical tree | IR1 produced. |
| Invalid NNF shape after normalization | IR1 invariant failure. |
