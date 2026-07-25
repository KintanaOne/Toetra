# Aggregated Assertion Set

> Status: Planned / Critical  
> Implementation: Not implemented yet  
> Scope: Composition of DSL assertions, semantic constraints, and model constraints

## Purpose

The `AggregatedAssertionSet` is the planned representation that combines all constraints required for verification.

A Toetra backend should not receive isolated DSL assertions only.

It should receive a complete verification problem composed from:

- user DSL assertions,
- scope constraints,
- semantic constraints,
- neighborhood constraints,
- domain constraints,
- ModelBridge-derived constraints,
- backend capability constraints when relevant.

---

## Why Aggregation Exists

A user writes a property such as:

```toetra
[ROBUSTNESS]: forall baseline, candidate => CLASSIFICATION.EQUAL()
```

But the backend needs more than the RHS predicate.

It needs to understand:

- which point is the anchor,
- which point is the perturbation,
- what distance bound applies,
- what model is being verified,
- what task the model performs,
- what output equality means,
- which features exist,
- which target is predicted,
- what backend capabilities are available.

The aggregation layer is where those elements become one verification problem.

---

## Conceptual Shape

```text
AggregatedAssertionSet
├── user_assertions
├── semantic_constraints
├── scope_constraints
├── domain_constraints
├── neighborhood_constraints
├── model_constraints
├── backend_constraints
├── preservation_metadata
└── traceability
```

---

## Constraint Sources

### User Assertions

Assertions directly expressed in the DSL.

Examples:

```text
age <= 30
CLASSIFICATION.EQUAL()
x'.score >= x.score
```

---

### Semantic Constraints

Constraints derived from semantic validation.

Examples:

```text
x is an anchor variable
x' is a perturbation variable
x0 is the symbolic variable declared by the quantified scope
implicit age resolves to x'.age
```

---

### Scope Constraints

Constraints derived from the property LHS.

Examples:

```text
property is local
property is pairwise
property is quantifier-based
```

---

### Neighborhood Constraints

Constraints derived from perturbation definitions.

Example:

```text
distance(x, x') <= eps
metric = L2
```

---

### Domain Constraints

Constraints derived from typed input-domain restrictions.

Examples:

```text
x0.a: [0.0, 3.0]
→ x0.a >= 0.0 AND x0.a <= 3.0
```

```text
x0.region: {EU, US}
→ x0.region == EU OR x0.region == US
```

Domain assumptions must use:

```text
AssumptionSource.DOMAIN
```

and preserve provenance to the source entry, subject, interval/set form, and generated atoms.

Domain assumptions are composed conjunctively with model assumptions and the verification query. Their internal finite-set expansion may contain disjunctions.

---

### Model Constraints

Constraints derived from ModelBridge.

Examples:

```text
feature age exists
feature age is numeric
model task is classification
model output is compatible with CLASSIFICATION.EQUAL
```

---

### Backend Constraints

Constraints derived from backend capability analysis.

Examples:

```text
backend supports linear constraints
backend supports classification equality
backend does not support unsupported nonlinear model type
```

---

## Input Contract

The aggregation layer should consume:

- IR2-normalized logical forms,
- `ScopeIR`,
- `ModelSchema`,
- semantic metadata,
- backend capability metadata where available.

---

## Output Contract

The output should be a complete verification problem, still backend-independent or backend-preparable depending on design.

It should not yet be a raw Z3 expression or backend-specific file.

---

## Invariants

A valid aggregated assertion set must satisfy:

| Invariant | Description |
|---|---|
| Complete context | User assertions must be accompanied by all required scope/model constraints. |
| No unresolved features | Feature references must be checked against model schema or explicitly deferred. |
| No duplicated contradictions without diagnostics | Contradictions should be detectable or tracked. |
| Traceability | Every generated constraint should be traceable to its source. |
| Backend independence | Aggregation should not prematurely encode solver-specific objects. |
| Semantic preservation | Aggregation must not alter user intent. |

---

## Relationship with Lowering

Aggregation creates the complete problem.

Lowering and minimization prepare it for backend encoding.

```text
AggregatedAssertionSet → LoweredQuery → BackendQuery
```

---

## Relationship with ModelBridge

ModelBridge provides `ModelSchema` and future model-derived constraints.

Aggregation is where those constraints meet the DSL query.

```text
IR2 query + ModelSchema constraints → AggregatedAssertionSet
```

---

## Relationship with Miova

Miova can challenge aggregation by mutating:

- missing model constraints,
- incompatible feature references,
- invalid domain constraints,
- contradictory assertions,
- corrupted traceability,
- duplicated constraints,
- invalid scope/model combinations.

This makes aggregation one of the most important future test surfaces.

---

## Summary

`AggregatedAssertionSet` is where Toetra stops treating the DSL and model separately.

It is the point where user intent, semantic context, and model reality become one verification problem.
