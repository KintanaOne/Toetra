# Syntax

> Status: Stabilizing  
> Scope: User-facing FORML syntax  
> Priority: P1  
> Audience: FORML users, test authors, documentation readers

## Purpose

This document describes the user-facing syntax of FORML specifications.

It focuses on how to write `.forml` files, not on how the compiler internally represents them.

A FORML specification describes behavioral properties that a machine learning model should satisfy.

---

## Minimal Program

A minimal FORML program declares a model, a target, and at least one property:

```forml
model := "model.joblib"
target := prediction

[BOUND]: check_at x => score >= 0
```

This program means:

```text
For the model declared in the header, evaluate a BOUND property at point x and assert that score is greater than or equal to zero.
```

---

## Header Syntax

The header provides global inputs to the verification pipeline.

```forml
model := "model.joblib"
target := prediction
```

Optional declarations may include:

```forml
dataset := "data.csv"
eps := 0.1
```

### Header Fields

| Field | Required | Example | Meaning |
|---|---:|---|---|
| `model` | yes | `model := "model.joblib"` | Model artifact to verify. |
| `target` | yes | `target := prediction` | Output or target of interest. |
| `dataset` | no | `dataset := "data.csv"` | Dataset used for schema inference. |
| variables | no | `eps := 0.1` | Reusable values. |

---

## Property Syntax

A property follows this shape:

```forml
[PROPERTY_TYPE]: scope => assertion using backend
```

The backend is optional.

Examples:

```forml
[ROBUSTNESS]: at x in neighborhood(metric=L2, eps=0.1) => CLASSIFICATION.EQUAL()

[BOUND]: check_at x => score >= 0

[MONOTONICITY]: x ~ x' in neighborhood(metric=L1, eps=1.0) => x'.score >= x.score
```

---

## Property Type Syntax

Property types are written between brackets:

```forml
[ROBUSTNESS]
[BOUND]
[FAIRNESS]
[MONOTONICITY]
[STABILITY]
[LOGIC]
```

The property type describes the user intent.

It does not alone define the full verification problem. The scope and assertion complete the property.

---

## Scope Syntax

### `check_at`

Pointwise evaluation:

```forml
[BOUND]: check_at x => score >= 0
```

Meaning:

```text
Evaluate the property at one point x.
```

---

### `at`

Local evaluation around an anchor:

```forml
[ROBUSTNESS]: at x in neighborhood(metric=L2, eps=0.1) => CLASSIFICATION.EQUAL()
```

Meaning:

```text
Evaluate robustness around anchor x using a perturbation x'.
```

Implicit feature references are resolved against `x'` by default.

---

### Pairwise

Pairwise relation between two variables:

```forml
[FAIRNESS]: x ~ x' in neighborhood(metric=L2, eps=0.1) => score == score
```

The intended pairwise syntax is:

```text
x ~ x'
```

The semantic layer interprets:

| Variable | Role |
|---|---|
| `x` | anchor |
| `x'` | perturbation / paired point |

---

### Quantifiers

Quantified evaluation:

```forml
[BOUND]: forall with age(18, 65) => score >= 0
```

Accepted quantifier forms should normalize to:

```text
forall
exists
```

Potential user-facing forms:

```text
forall
exists
∀
∃
```

---

## Neighborhood Syntax

Neighborhoods define perturbation spaces.

```forml
in neighborhood(metric=L2, eps=0.1)
```

Examples:

```forml
in neighborhood(metric=L1, eps=1.0)
in neighborhood(metric=L2, eps=0.1)
in neighborhood(metric=Linf, eps=0.05)
```

The most important argument is usually:

| Argument | Meaning |
|---|---|
| `eps` | Perturbation radius or tolerance. |

---

## Domain Syntax

Domains restrict evaluation to a set of values.

```forml
with age(18, 65)
with segment("A", "B")
```

A domain can be attached to supported scopes:

```forml
[BOUND]: forall with age(18, 65) => score >= 0
```

Domain semantics are not only syntactic. They must later be interpreted by semantic validation and IR lowering.

---

## Assertion Syntax

Assertions describe what must hold.

### Comparisons

```forml
score >= 0
age <= 65
prediction == 1
```

### Boolean composition

```forml
score >= 0 AND score <= 1
```

```forml
NOT age < 18
```

```forml
age >= 18 OR segment == "adult"
```

### Implication

```forml
age >= 18 -> score >= 0.5
```

### Parentheses

```forml
(age >= 18 AND age <= 65) -> score >= 0.5
```

### Problem predicates

```forml
CLASSIFICATION.EQUAL()
REGRESSION.BETWEEN()
```

---

## Backend Syntax

A property can optionally specify a backend:

```forml
[ROBUSTNESS]: at x in neighborhood(metric=L2, eps=0.1) => CLASSIFICATION.EQUAL() using z3
```

With arguments:

```forml
using z3(timeout=30)
```

The backend syntax is a request or hint. The backend boundary still validates compatibility before execution.

---

## Recommended Formatting Style

Recommended style for readability:

```forml
model := "model.joblib"
target := prediction
dataset := "data.csv"

[ROBUSTNESS]: at x in neighborhood(metric=L2, eps=0.1)
  => CLASSIFICATION.EQUAL()
  using z3

[BOUND]: check_at x
  => score >= 0 AND score <= 1
```

This style is not necessarily required by the parser, but it improves readability and documentation consistency.

---

## Invalid Syntax Examples

### Missing header

```forml
[BOUND]: check_at x => score >= 0
```

Invalid because `model` and `target` are missing.

### Missing assertion

```forml
[BOUND]: check_at x =>
```

Invalid because the property has no RHS assertion.

### Invalid pairwise form

```forml
[FAIRNESS]: x ~ y in neighborhood(metric=L2, eps=0.1) => score == score
```

The semantic layer expects the right variable to be the primed version of the left variable, such as `x'`.

---

## Related Documents

- [Grammar](grammar.md)
- [Properties](properties.md)
- [Scopes](scopes.md)
- [Assertions](assertions.md)
- [Backends Syntax](backends.md)
- [Examples](examples.md)
