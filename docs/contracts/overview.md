# Contracts Overview

> Status: P0 / Active architecture baseline  
> Scope: FORML artifact boundaries and verification contracts  
> Implementation: Mixed — implemented, stabilizing and target contracts  
> Audience: maintainers, contributors, backend authors and Miova campaign authors

## Purpose

FORML is organized as a sequence of explicit artifact transformations.

A contract answers:

```text
What must be true before this transformation?
What must be preserved by it?
What may the next layer rely on?
Which layer owns each rejection?
```

Contracts prevent the compiler from becoming a chain of ad-hoc conversions and make documentation-first changes executable as testable obligations.

---

## Contracted Pipeline

```text
.forml source
→ CST
→ AST
→ SemanticValidatedAST
→ IR1
→ IR2 normal forms + assumptions
→ Aggregated verification condition
→ BackendQuery
→ VerificationResult
```

ModelBridge contributes:

```text
model artifact
→ ModelSchema
→ model assumptions
→ aggregated verification condition
```

---

## Language-Evolution Contract

The normative cross-layer contract for explicit quantifiers, typed domains and scalar expressions is:

```text
contracts/quantified-domain-scalar-expressions.md
```

It consolidates ADR-0013, ADR-0014 and ADR-0015 into boundary-level obligations.

---

## Contract Categories

| Category | Main documents | Purpose |
|---|---|---|
| Syntax | `source-to-cst`, `cst-to-ast`, `ast-contract` | Preserve legal syntax as typed domain objects. |
| Semantics | `ast-to-semantic`, `schema-to-semantic` | Resolve binding, types, scopes and model meaning. |
| Logical IR | `semantic-to-ir1`, `ir1-to-ir2` | Preserve meaning while normalizing logic. |
| Composition | `assertion-aggregation`, `model-constraints` | Build the complete verification condition. |
| Backend | `ir-to-backend`, `lowering-minimization` | Check capabilities and produce solver artifacts. |
| Cross-cutting | `errors`, `type-normalization`, `mutation-boundaries` | Stabilize diagnostics, types and validation campaigns. |

---

## Required Contract Sections

Every boundary contract should state:

- purpose;
- input and preconditions;
- output and postconditions;
- information-preservation requirements;
- invariants;
- non-goals;
- failure ownership;
- current implementation gap when relevant;
- mutation/testing hooks.

---

## Preservation Principle

Every transformation must preserve user intent until a documented semantic rewrite occurs.

In particular:

- quantified identifiers are never replaced silently;
- interval boundary kinds are never reduced to ambiguous booleans;
- finite sets are never confused with intervals;
- scalar expressions are never flattened to text;
- unsupported arithmetic is never approximated silently;
- domain assumptions retain provenance;
- `forall` and `exists` never share the same result interpretation accidentally.

---

## Current and Target Labels

| Label | Meaning |
|---|---|
| Implemented | Present and exercised in the current codebase. |
| Stabilizing | Present but still gaining stricter contracts or diagnostics. |
| Accepted target | Semantics are decided; implementation may still be pending. |
| Deferred | Deliberately outside the current implementation scope. |

A target contract is authoritative for planned changes but must not be described as already implemented.

---

## Relationship with Miova

Miova is external to normal verification execution.

It may challenge each artifact boundary and assert:

```text
valid mutation   → accepted and preserved
invalid mutation → rejected at the owning boundary
wrong-boundary rejection → contract failure
silent reinterpretation  → contract failure
```
