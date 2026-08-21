# Model IR Test Matrix

> Status: Stabilized for Affine Model IR, construction, and compiler lowering
>
> Scope: Model IR invariants, structural validity, immutability, and deterministic normalization

## Purpose

This document defines the test matrix for Toetra Model IR implementations.

The goal is to ensure that every successfully constructed Model IR is a valid,
immutable, deterministic representation of supported model computation.

This matrix complements the Model IR contract and ADR-0034.

## General testing principles

Every Model IR family must test:

- valid construction;
- family-specific structural invariants;
- immutability;
- deterministic structural equality;
- rejection of invalid numeric parameters where applicable;
- independence from framework, verification, and backend-specific objects.

A successfully constructed Model IR should not require defensive revalidation by
downstream compiler components.

## Affine Model IR

An affine model represents a computation of the form:

```text
f(x) = Σ wi * xi + b
```

Each affine term explicitly associates one feature identifier with one
coefficient.

Conceptually:

```text
AffineModelIR
├── terms
│   ├── (feature_0, coefficient_0)
│   ├── (feature_1, coefficient_1)
│   └── ...
└── bias
```

### Construction and structural validity

| ID | Scenario | Example | Expected result | Contract covered |
|---|---|---|---|---|
| AFF-001 | Valid affine representation | `(("age", 0.7), ("income", -0.2))`, bias `1.0` | Accepted | Valid construction |
| AFF-002 | Zero coefficient | `(("age", 0.0),)` | Accepted | Finite coefficients |
| AFF-003 | Zero bias | bias `0.0` | Accepted | Finite bias |
| AFF-004 | Negative coefficient | `(("age", -1.5),)` | Accepted | Finite coefficients |
| AFF-005 | Negative bias | bias `-2.5` | Accepted | Finite bias |
| AFF-006 | Empty term sequence | `()`, bias `3.0` | Accepted by the Model IR contract | Constant affine function |
| AFF-007 | Duplicate feature identifier | `(("age", 1.0), ("age", 2.0))` | Rejected | Unique feature identifiers |
| AFF-008 | Empty feature identifier | `("", 1.0)` | Rejected | Valid feature identifier |
| AFF-009 | Whitespace-only feature identifier | `("   ", 1.0)` | Rejected | Valid feature identifier |

### Numeric validity

| ID | Scenario | Example | Expected result | Contract covered |
|---|---|---|---|---|
| AFF-010 | `NaN` coefficient | `(("age", NaN),)` | Rejected | Finite coefficients |
| AFF-011 | Positive infinite coefficient | `(("age", +inf),)` | Rejected | Finite coefficients |
| AFF-012 | Negative infinite coefficient | `(("age", -inf),)` | Rejected | Finite coefficients |
| AFF-013 | `NaN` bias | bias `NaN` | Rejected | Finite bias |
| AFF-014 | Positive infinite bias | bias `+inf` | Rejected | Finite bias |
| AFF-015 | Negative infinite bias | bias `-inf` | Rejected | Finite bias |

These tests concern model parameters only.

They do not define Toetra's policy for `NaN`, infinite, or missing values in
runtime input data. Input-data validity belongs to preprocessing, dataset,
domain, or runtime validation.

### Immutability

| ID | Scenario | Expected result | Contract covered |
|---|---|---|---|
| AFF-016 | Reassign `bias` after construction | Impossible / rejected | Model IR immutability |
| AFF-017 | Reassign `terms` after construction | Impossible / rejected | Model IR immutability |
| AFF-018 | Mutate the term sequence in place | Impossible | Immutable term sequence |
| AFF-019 | Mutate an individual affine term | Impossible | Immutable affine terms |

Immutability is transitive for all values that define model computation.

An immutable outer Model IR object must not expose mutable internal structures
whose modification could change the represented computation.

### Ordering and determinism

| ID | Scenario | Expected result | Contract covered |
|---|---|---|---|
| AFF-020 | Construct with terms in a given order | Order is preserved | Stable term order |
| AFF-021 | Read terms repeatedly | Same order is observed | Deterministic representation |
| AFF-022 | Two representations with identical ordered terms and bias | Structurally equal | Deterministic equality |
| AFF-023 | Same feature/coefficient pairs in a different order | Representations remain distinguishable structurally unless normalization occurred before construction | Stable normalized order |

`AffineModelIR` must not silently reorder its terms.

The Model IR builder preserves or derives the canonical source-model order
before constructing the Model IR.

The initial sklearn affine builder additionally tests fitted-model detection,
single-output shape, exact supported estimator types, schema/model identity,
feature count and order alignment, deterministic term construction, and
non-finite parameter rejection.

## Boundary cases not owned by Affine Model IR

The following cases must not be tested as Affine Model IR invariants:

| Scenario | Owning layer |
|---|---|
| Input dataset contains `NaN` | Dataset / preprocessing / runtime |
| Input dataset contains missing values | Dataset / preprocessing / runtime |
| Symbolic input domain permits unsupported values | Semantic / verification-domain validation |
| Feature is absent from a particular runtime point | Model evaluation / compiler lowering |
| Model family does not support a requested observable | Model-semantic lowering |
| Backend cannot represent a valid affine constraint | Numeric compatibility / backend |

## Future Model IR families

New Model IR families must add their own matrix to this document before or with
their implementation.

Expected future sections include:

```text
Tree Model IR
Tree Ensemble Model IR
```

Their matrices must follow the same structure:

1. valid construction;
2. structural invariant violations;
3. numeric validity where applicable;
4. immutability;
5. deterministic representation;
6. family-specific boundary conditions.

## Exit criteria for Affine Model IR

The Affine Model IR implementation is considered structurally stabilized when:

- all `AFF-*` tests defined as in-scope are implemented;
- every invalid state is rejected at construction time;
- every valid instance is immutable after construction;
- structural equality is deterministic;
- term order is preserved;
- no Affine Model IR test requires sklearn, IR1, IR2, Z3, or another backend.

At that point, downstream components may treat an `AffineModelIR` instance as a
trusted normalized representation of affine computation.

These criteria are satisfied. Runtime migration additionally tests:

- construction directly from fitted sklearn affine models;
- schema-only compatibility construction through normalized metadata;
- structural equality between legacy and Model IR-derived regression IR2;
- structural equality between legacy and Model IR-derived binary-logistic IR2;
- default runtime use of Model IR construction and compiler lowering;
- rejection of non-finite parameters before compatibility routing or backend
  translation;
- absence of direct Model IR imports from backend packages.
