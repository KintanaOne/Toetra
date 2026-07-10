# Scope IR

> Status: Implemented / Stabilizing  
> Implementation: IR1 scope representation  
> Scope: Semantic context lowering

## Purpose

`ScopeIR` represents where and how a FORML property is evaluated.

It is produced from the left-hand side of a property after semantic validation.

In the DSL, scope can be expressed through constructs such as:

- `check_at`,
- `at`,
- `pairwise`,
- `forall`,
- `exists`.

`ScopeIR` turns those syntactic forms into explicit semantic context.

---

## Conceptual Shape

```text
ScopeIR
├── kind
├── variables
├── neighborhood
└── domain
```

| Field | Role |
|---|---|
| `kind` | Scope category: pointwise, local, pairwise, quantifier. |
| `variables` | Mapping from variables to semantic roles. |
| `neighborhood` | Optional perturbation or distance context. |
| `domain` | Optional domain restriction. |

---

## Scope Kinds

### Pointwise Scope

Pointwise scope evaluates a property at a single point.

DSL example:

```forml
[BOUND]: check_at x => age <= 30
```

Conceptual IR:

```text
kind = pointwise
variables = { "x": "anchor" }
```

---

### Local Scope

Local scope evaluates a property around a point and introduces an implicit perturbation variable.

DSL example:

```forml
[ROBUSTNESS]: at x in neighborhood(metric=L2, eps=0.1) => CLASSIFICATION.EQUAL()
```

Conceptual IR:

```text
kind = local
variables = {
  "x": "anchor",
  "x'": "perturbation"
}
```

Implicit feature access should resolve to the perturbation variable unless explicitly specified.

---

### Pairwise Scope

Pairwise scope compares an anchor and a primed counterpart.

DSL example:

```forml
[MONOTONICITY]: x ~ x' in neighborhood(metric=L2, eps=0.1) => x'.score >= x.score
```

Conceptual IR:

```text
kind = pairwise
variables = {
  "x": "anchor",
  "x'": "perturbation"
}
```

The pairwise convention must remain consistent with the semantic validator.

---

### Quantifier Scope

Quantifier scope introduces an explicitly named symbolic variable.

DSL example:

```forml
[BOUND]: forall applicant => applicant.age >= 18
```

Conceptual IR:

```text
kind = quantifier
variables = {
  "applicant": "symbolic"
}
quantifier = forall
```

The identifier is preserved from source to `ScopeIR`. It must not be replaced by `_x`. Implicit features use the same identifier as their resolved entity.

---

## Neighborhood IR

Neighborhoods define perturbation spaces.

Conceptually:

```text
NeighborhoodIR
├── metric
├── eps
└── args
```

Examples:

- L1 ball,
- L2 ball,
- Linf ball,
- future custom perturbation domains.

The `eps` value should be normalized as a numeric value.

---

## Domain IR

`DomainIR` represents validated, backend-independent input admissibility constraints.

Target conceptual shape:

```text
DomainIR
├── constraints
│   ├── IntervalConstraintIR
│   │   ├── entity
│   │   ├── feature
│   │   ├── lower
│   │   ├── upper
│   │   ├── lower_boundary
│   │   └── upper_boundary
│   └── FiniteSetConstraintIR
│       ├── entity
│       ├── feature
│       └── values
└── provenance
```

Example:

```text
DomainIR(
  constraints=(
    IntervalConstraintIR(x0.a, 0.0, 3.0, CLOSED, OPEN),
    FiniteSetConstraintIR(x0.region, (EU, US)),
  )
)
```

Invariants:

- every subject is semantically resolved;
- interval boundary kinds are explicit;
- finite-set members retain their semantic literal kinds;
- constraints are conjunctive at the domain level;
- no generic domain name or ad-hoc args dictionary is required;
- no backend-specific expression appears in `DomainIR`.

`DomainIR` is later expanded into `AssumptionIR2(source=DOMAIN)` formulas. The scope representation itself should remain readable and traceable.

---

## Invariants

A valid `ScopeIR` must satisfy:

| Invariant | Description |
|---|---|
| Known kind | Scope kind must be one of the supported semantic scopes. |
| Explicit variables | No implicit variable should remain unresolved. |
| Role consistency | Variable roles must match semantic validation. |
| Neighborhood consistency | Neighborhoods must be valid for the scope kind. |
| Domain consistency | Domain restrictions must be represented without raw syntax leakage. |
| Semantic preservation | The scope must preserve LHS semantics from the DSL. |

---

## Current Stabilization Points

The current implementation already represents scope information, but several points should be stabilized:

- pairwise parsing must split `x ~ x'` consistently, not comma-separated pairs;
- quantifier scope must preserve the exact identifier declared in the source;
- pointwise role naming should align with semantic roles;
- typed domain constraints should replace ad-hoc name/argument dictionaries;
- metrics should be normalized with official vocabulary values.

---

## Relationship with SemanticContext

`SemanticContext` is produced during semantic validation.

`ScopeIR` is its IR-level projection.

```text
SemanticContext → ScopeIR
```

`SemanticContext` is validation-oriented.  
`ScopeIR` is compilation-oriented.

---

## Relationship with ModelBridge

ModelBridge can enrich scope validation by checking that referenced features, targets, and dtypes exist in the model schema.

Future schema-aware semantic validation should ensure that `ScopeIR` does not refer to model features that cannot exist.

---

## Relationship with Miova

Scope is a high-value mutation surface.

Miova can mutate:

- scope kind,
- variable roles,
- primed variable conventions,
- neighborhood metrics,
- epsilon values,
- domain values,
- missing or incompatible scope metadata.

Expected behavior should be either valid transformation, semantic rejection, or contract failure depending on the mutation.

---

## Summary

`ScopeIR` formalizes the evaluation context of a FORML property.

It is the bridge between LHS semantics and logical verification.
