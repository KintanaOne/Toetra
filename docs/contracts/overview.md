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

## Point-Binding and Evaluation Contract

The normative target contract for anchors, ordered and nested binders, point-indexed model evaluations, local sugar, multi-point evidence and replay is:

```text
contracts/point-binding-and-evaluation.md
```

It operationalizes ADR-0017 across the complete compiler, ModelBridge, backend and runtime pipeline. Until implementation patches land, it is an accepted target contract rather than a claim about current behavior.

---

## Model Output and Classification Contracts

The implemented Patch 21 public contracts are:

- [Model Output Observables](model-output-observables.md), separating output ports,
  model evaluations, public observables, and internal quantities;
- [Model Semantic Lowering](model-semantic-lowering.md), defining the only boundary
  where a declarative observable may become model-family-specific constraints;
- [Initial Binary Classification Profile](binary-classification-profile.md),
  freezing the first logistic binary route and its decision boundary.
- [Model Output Reporting and Replay](output-reporting-and-replay.md),
  preserving source intent, formal reconstruction, observer-based concrete replay,
  and the additive JSON v5 evidence contract.

These contracts are public in `1.0.0rc2` for the direct fitted binary sklearn
`LogisticRegression` route. They do not generalize support to other classifiers,
wrappers, thresholds, frameworks, or backends.

---

## Numeric Compatibility Contract

The backend-neutral contract for framework/model profiles, ModelBridge encoders, backend numeric profiles, deterministic rule resolution and permitted conclusions is:

- [Numeric Compatibility Registry](numeric-compatibility-registry.md)
- [Numeric Compatibility Reporting](numeric-compatibility-reporting.md)
- [Generated Numeric Compatibility Matrices](../generated/numeric-compatibility-matrices.md)

Together they operationalize ADR-0018 without making sklearn or Z3 the architectural abstraction.

---

## Verification Provenance Contract

The [Verification Provenance Contract](verification-provenance.md) defines content-addressed artifact evidence, completeness, software/compiler identity and the five fingerprints exported by JSON schema v5.

## Public V1 Contract

The [Public V1 Contract](public-v1-contract.md) freezes the supported Python facade, executable framework/model/backend profile, JSON v5 compatibility rules, result semantics, license alignment and release gates for the FORML 1.x line.

## Contract Categories

| Category | Main documents | Purpose |
|---|---|---|
| Syntax | `source-to-cst`, `cst-to-ast`, `ast-contract` | Preserve legal syntax as typed domain objects. |
| Semantics | `ast-to-semantic`, `schema-to-semantic`, `model-output-observables`, `model-semantic-lowering` | Resolve binding, typed observables, scopes and model meaning. |
| Logical IR | `semantic-to-ir1`, `ir1-to-ir2` | Preserve meaning while normalizing logic. |
| Composition | `assertion-aggregation`, `model-constraints`, `binary-classification-profile` | Build the complete verification condition under an explicit model profile. |
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

## Specification Constant Contract

The cross-layer rules for immutable user declarations and bare-name resolution are defined in:

- [Specification Constants Contract](specification-constants.md)

This contract is authoritative for AST shape, semantic lookup order, type preservation, provenance and backend treatment.


## Backend execution

The [Backend Execution Contract](backend-execution-contract.md) defines portable timeout, resource, cancellation, deterministic execution and termination evidence for every backend adapter.

## Release artifacts

See [Release engineering contract](release-engineering.md).
