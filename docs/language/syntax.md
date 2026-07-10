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

Quantified evaluation introduces an explicitly named symbolic input variable:

```forml
[BOUND]: forall x0 => target >= 0
```

```forml
[BOUND]: exists candidate => candidate.score > 0
```

Word and Unicode forms normalize to the same internal quantifier values:

```text
forall x0
∀ x0
exists x0
∃ x0
```

The identifier is mandatory and must be preserved across the compiler pipeline. Explicit input references in the domain or assertion must resolve to that identifier. Implicit feature references use it as the default entity. `target` remains a model-output reference and does not need to repeat the input identifier.

See [Quantified Variable Bindings](quantified-bindings.md) for the normative binding rules.

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

Domains restrict admissible input valuations.

```forml
with domain(
    x0.a: [0.0, 3.0],
    x0.b: {obj1, obj2},
    x0.c: ]0.0, 3.0],
    x0.d: {0.0, 7.0},
    x0.e: ]0.0, 3.0[
)
```

A domain entry has the shape:

```text
qualified_attribute : domain_constraint
```

The subject must be explicit:

```forml
x0.age: [18, 65]
```

This is invalid:

```forml
age: [18, 65]
```

### Interval forms

| Syntax | Lower bound | Upper bound |
|---|---|---|
| `[a, b]` | closed | closed |
| `]a, b]` | open | closed |
| `[a, b[` | closed | open |
| `]a, b[` | open | open |

Bounds may be arithmetic expressions:

```forml
with domain(
    x0.a: [x0.b - 1.0, x0.b + 1.0],
    x0.b: [0.0, 10.0]
)
```

All input references inside a domain are explicit. `target` is not permitted in a domain bound.

### Finite sets

```forml
x0.segment: {obj1, obj2}
x0.level: {0.0, 7.0}
```

Curly braces always denote a finite discrete set. Finite-set members remain literals; arithmetic members are not part of this patch.

### Binding and composition

Every domain reference must resolve to a variable introduced by the enclosing scope. Entries are conjoined and interpreted simultaneously rather than evaluated in declaration order.

See [Domains](domains.md) and [Arithmetic Expressions](arithmetic-expressions.md).

## Assertion Syntax

Assertions are logical predicates built from comparisons and problem-level predicates.

### Comparisons

The general comparison form is:

```text
scalar_expression comparison_operator scalar_expression
```

Examples:

```forml
target >= 0
x0.age == 42
x0.a + x0.b <= 7
2 * target >= x0.a - 1
```

Supported comparison operators:

```text
== != < <= > >=
```

### Arithmetic expressions

Arithmetic operators:

```text
unary +  unary -  *  /  +  -
```

Example:

```forml
2 * x0.a + x0.b <= target
```

The initial verification profile is affine: multiplication by a constant and division by a non-zero constant are supported. Symbolic products and symbolic denominators require future capabilities.

### Boolean composition

```forml
x0.a >= 0 AND x0.b <= 1
x0.segment == "A" OR x0.segment == "B"
NOT target < 0
```

### Logical implication

```forml
x0.age >= 18 -> target >= 0.5
```

### Parentheses

```forml
(x0.a + x0.b <= 7 AND target >= 0) OR target == -1
```

### Invalid chained comparison

```forml
0 <= x0.a <= 3
```

Write instead:

```forml
0 <= x0.a AND x0.a <= 3
```

### Problem predicates

```forml
CLASSIFICATION.EQUAL()
REGRESSION.BETWEEN()
```

Problem predicates are boolean leaves and cannot be used as arithmetic operands.

See [Assertions](assertions.md) and [Arithmetic Expressions](arithmetic-expressions.md).

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
- [Domains](domains.md)
- [Quantified Variable Bindings](quantified-bindings.md)
- [Assertions](assertions.md)
- [Arithmetic Expressions](arithmetic-expressions.md)
- [Backends Syntax](backends.md)
- [Examples](examples.md)
