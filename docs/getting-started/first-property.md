# First FORML Property

> Status: Draft  
> Scope: DSL onboarding  
> Implementation: Syntax subject to stabilization

## Purpose

This page introduces the shape of a minimal FORML property.

A FORML program contains a header and one or more property sections.

## Minimal structure

```forml
model := "model.joblib"
target := prediction

[BOUND]:
check_at x => score <= 1.0 using z3
```

This example should be read as:

```text
For the model declared in the header,
check a bounded property at a point x,
and use Z3 as the verification backend.
```

## Header

The header identifies the model and target.

```forml
model := "model.joblib"
target := prediction
```

| Field | Purpose |
|---|---|
| `model` | Path or identifier for the model artifact |
| `target` | Target or prediction output to reason about |

A dataset declaration may also be introduced when schema inference is required.

## Property type

Property types describe the kind of behavior being checked.

Examples:

```forml
[ROBUSTNESS]
[BOUND]
[MONOTONICITY]
[FAIRNESS]
[STABILITY]
[LOGIC]
```

## Scope

The scope describes where the property applies.

Examples:

```forml
check_at x
at x in neighborhood(metric=L2, eps=0.1)
x ~ x' in neighborhood(metric=L2, eps=0.1)
forall with domain(...)
exists with domain(...)
```

## Assertion

The assertion describes what must hold.

Examples:

```forml
score <= 1.0
age >= 18 AND score <= 0.9
NOT risk > 0.8
CLASSIFICATION.EQUAL()
```

## Backend

For V1, the backend should be Z3.

```forml
using z3
```

Other backends such as ERAN are post-V1 extensions.

## What happens internally?

The property is transformed through the FORML pipeline:

```text
source
→ CST
→ AST
→ SemanticValidatedAST
→ IR1
→ IR2
→ AggregatedAssertionSet
→ LoweredQuery
→ Z3 BackendQuery
```

## Stabilization note

This page should be updated alongside the grammar and golden samples.

The examples should eventually be executable as integration test.
