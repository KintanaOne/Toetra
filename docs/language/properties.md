# Properties

> Status: Stabilizing  
> Scope: Property types and their intended semantics  
> Priority: P1  
> Audience: DSL users, semantic layer contributors, verification backend authors

## Purpose

A FORML property expresses a behavioral guarantee that a model should satisfy.

Every property combines:

```text
property type
+ evaluation scope
+ assertion
+ optional backend selection
```

Example:

```forml
[ROBUSTNESS]: at x in neighborhood(metric=L2, eps=0.1) => CLASSIFICATION.EQUAL()
```

This expresses a robustness intent evaluated around an anchor point `x`.

---

## Property Structure

A property section has the following shape:

```forml
[PROPERTY_TYPE]: scope => assertion using backend
```

The backend is optional.

| Element | Role |
|---|---|
| `PROPERTY_TYPE` | Declares the kind of behavioral guarantee. |
| `scope` | Defines where the property is evaluated. |
| `assertion` | Defines what must hold. |
| `backend` | Optional verification backend request. |

---

## Supported Property Types

### `ROBUSTNESS`

Robustness properties express that model behavior should remain stable under controlled perturbations.

Example:

```forml
[ROBUSTNESS]: at x in neighborhood(metric=L2, eps=0.1) => CLASSIFICATION.EQUAL()
```

Typical scopes:

| Scope | Status |
|---|---|
| `at` | supported |
| `check_at` | supported |
| quantifier | supported |

Typical future backend requirements:

- model constraints,
- perturbation constraints,
- output equivalence constraints,
- solver or verifier encoding.

---

### `STABILITY`

Stability properties express that model behavior should remain consistent under controlled conditions.

Example:

```forml
[STABILITY]: at x in neighborhood(metric=L2, eps=0.05) => REGRESSION.BETWEEN()
```

Stability is close to robustness, but may be used for broader behavioral persistence guarantees.

Typical scopes:

| Scope | Status |
|---|---|
| `at` | supported |
| quantifier | supported |

---

### `FAIRNESS`

Fairness properties express behavioral constraints between points, groups, or comparable situations.

Example:

```forml
[FAIRNESS]: x ~ x' in neighborhood(metric=L2, eps=0.1) => CLASSIFICATION.EQUITY()
```

Typical scope:

| Scope | Status |
|---|---|
| pairwise | supported |

Fairness will likely require ModelBridge and domain-aware constraints to become fully meaningful.

---

### `MONOTONICITY`

Monotonicity properties express that outputs should move in a consistent direction when a feature or condition changes.

Example:

```forml
[MONOTONICITY]: x ~ x' in neighborhood(metric=L1, eps=1.0) => REGRESSION.INCREASING()
```

Typical scopes:

| Scope | Status |
|---|---|
| pairwise | supported |
| quantifier | supported |

Monotonicity is a strong candidate for IR2 and backend-specific lowering because it often requires comparing two symbolic states. Attribute-to-attribute monotonicity forms such as `x'.score >= x.score` should remain marked as planned until the comparison AST supports right-hand-side attributes.

---

### `BOUND`

Bound properties express that a feature, score, probability, or output must remain within a range.

Examples:

```forml
[BOUND]: check_at x => score >= 0
```

```forml
[BOUND]: check_at x => score >= 0 AND score <= 1
```

Typical scopes:

| Scope | Status |
|---|---|
| `check_at` | supported |
| quantifier | supported |

---

### `LOGIC`

Logic properties express general logical assertions.

Example:

```forml
[LOGIC]: check_at x => (age >= 18 AND score >= 0.5) -> approved == true
```

`LOGIC` is useful for testing the compiler and expressing backend-independent logical relationships.

Its exact semantic compatibility rules should be stabilized before public freeze.

---

## Property and Scope Compatibility

Not every property type is compatible with every scope.

Current semantic compatibility should be documented as:

| Property | Supported Scopes |
|---|---|
| `ROBUSTNESS` | `local`, `pointwise`, `quantifier` |
| `STABILITY` | `local`, `quantifier` |
| `FAIRNESS` | `pairwise` |
| `MONOTONICITY` | `pairwise`, `quantifier` |
| `BOUND` | `pointwise`, `quantifier` |
| `LOGIC` | to define |

This compatibility is not a grammar concern. It is enforced by semantic validation.

---

## Property and Problem Predicates

Some properties use problem-level predicates:

```forml
[ROBUSTNESS]: forall baseline, candidate => CLASSIFICATION.EQUAL()
REGRESSION.BETWEEN()
```

For the executable binary profile, `CLASSIFICATION.EQUAL()` requires exactly two visible model-input points and is sugar for explicit label equality.

These predicates must be validated against:

- the declared or inferred ML task,
- the model schema,
- the property type,
- the backend capability.

Current compatibility examples:

| Problem | Compatible Functions |
|---|---|
| `CLASSIFICATION` | `EQUAL`, `EQUITY`, `BETWEEN` |
| `REGRESSION` | `EQUAL`, `INCREASING`, `DECREASING`, `BETWEEN` |

---

## Current vs Target Semantics

| Layer | Current Role | Target Role |
|---|---|---|
| Grammar | Accept property syntax. | Stable public DSL. |
| Builder | Build `PropertyNode`. | Fully canonical AST property nodes. |
| Semantic layer | Validate scope and compatibility. | Model-aware property validation. |
| IR1 | Represent backend-independent logical task. | NNF-normalized task representation. |
| IR2 | implemented / stabilizing | NNF/CNF/DNF, assumptions, requirements and verification conditions. |
| Backend lowering | implemented for Z3 affine profile | Capability-checked numeric-affine translation and execution. |

---

## Testing Requirements

Each property type should have:

- at least one valid grammar sample,
- at least one valid semantic sample,
- at least one invalid scope sample,
- at least one golden IR1 sample,
- future IR2 samples,
- future backend query samples,
- Hypothesis strategies,
- Miova mutation scenarios.

---

## Related Documents

- [Scopes](scopes.md)
- [Assertions](assertions.md)
- [Vocabulary](vocabulary.md)
- [Examples](examples.md)
