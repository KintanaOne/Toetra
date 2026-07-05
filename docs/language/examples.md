# Examples

> Status: Stabilizing  
> Scope: User-facing language examples and future golden samples  
> Priority: P1  
> Audience: FORML users, test authors, documentation readers

## Purpose

This document provides example FORML specifications.

Examples serve three roles:

1. Help users understand the DSL.
2. Provide documentation samples.
3. Become future golden samples for parser, builder, semantic, IR, and end-to-end test.

Each example should eventually define expected outputs at several layers:

```text
source
→ CST
→ AST
→ SemanticValidatedAST
→ IR1
→ IR2
→ AggregatedAssertionSet
→ BackendQuery
```

---

## Minimal Bound Check

```forml
model := "model.joblib"
target := prediction

[BOUND]: check_at x => score >= 0
```

### Intent

Ensure that `score` is non-negative at a given point.

### Expected Scope

```text
kind: pointwise
variables:
  x: anchor
default_entity: x
```

### Expected Assertion

```text
x.score >= 0
```

---

## Bounded Score Range

```forml
model := "model.joblib"
target := prediction

[BOUND]: check_at x => score >= 0 AND score <= 1
```

### Intent

Ensure that the model score remains in `[0, 1]`.

### Expected Logical Shape

```text
AND(
  x.score >= 0,
  x.score <= 1
)
```

---

## Local Robustness

```forml
model := "classifier.joblib"
target := prediction

dataset := "data.csv"

[ROBUSTNESS]: at x in neighborhood(metric=L2, eps=0.1) => CLASSIFICATION.EQUAL()
```

### Intent

Ensure classification output remains stable for perturbations around `x`.

### Expected Scope

```text
kind: local
variables:
  x: anchor
  x': perturbation
default_entity: x'
neighborhood:
  metric: L2
  eps: 0.1
```

### Target End-to-End Meaning

```text
For all perturbations x' around x within an L2 epsilon ball,
the classification output should remain equal.
```

---

## Pointwise Logical Rule

```forml
model := "model.joblib"
target := approved

[LOGIC]: check_at x => (age >= 18 AND income >= 1000) -> approved == true
```

### Intent

Express a conditional behavioral rule.

### Expected Logical Shape

```text
IMPLY(
  AND(
    x.age >= 18,
    x.income >= 1000
  ),
  x.approved == true
)
```

### IR1 Target

IR1 should normalize implication and negation according to the IR1-NNF contract.

---

## Pairwise Monotonicity

```forml
model := "regressor.joblib"
target := score

[MONOTONICITY]: x ~ x' in neighborhood(metric=L1, eps=1.0) => REGRESSION.INCREASING()
```

### Intent

Compare two related points and express a monotonicity constraint through a problem-level predicate.

### Expected Scope

```text
kind: pairwise
variables:
  x: anchor
  x': perturbation
default_entity: x'
```

### Expected Assertion

```text
ProblemIR(problem=REGRESSION, function=INCREASING)
```

### Planned Extension

A future attribute-to-attribute form such as `x'.score >= x.score` is useful, but it requires extending the comparison AST, builder, semantic validation, and IR contracts so the right-hand side can be an `AttributeNode`, not only a constant.

---

## Quantified Bound

```forml
model := "model.joblib"
target := prediction

[BOUND]: forall with age(18, 65) => score >= 0
```

### Intent

Ensure a bound for all symbolic inputs in a domain.

### Expected Scope

```text
kind: quantifier
variables:
  _x: symbolic
default_entity: _x
domain:
  age: [18, 65]
```

### Expected Assertion

```text
_x.score >= 0
```

---

## Regression Stability

```forml
model := "regressor.joblib"
target := prediction

[STABILITY]: at x in neighborhood(metric=L2, eps=0.05) => REGRESSION.BETWEEN()
```

### Intent

Ensure regression output remains inside a controlled range under local perturbation.

### Future Requirements

This example requires:

- model task detection,
- regression function compatibility,
- ModelBridge constraints,
- backend-specific output encoding.

---

## Backend Selection Example

```forml
model := "model.joblib"
target := prediction

[BOUND]: check_at x => score >= 0 using z3(timeout=30)
```

### Intent

Request Z3 as the verification backend.

### Expected Compiler Behavior

```text
Parse backend syntax
→ build BackendNode
→ normalize backend name
→ attach backend to IR task
→ validate backend capability before lowering
```

---

## Invalid Example: Missing Header

```forml
[BOUND]: check_at x => score >= 0
```

Expected failure:

```text
source-to-cst or builder boundary rejects missing header declarations.
```

---

## Invalid Example: Unknown Variable

```forml
model := "model.joblib"
target := prediction

[BOUND]: check_at x => y.score >= 0
```

Expected failure:

```text
semantic binding rejects y because only x exists in the scope.
```

---

## Invalid Example: Property/Scope Mismatch

```forml
model := "model.joblib"
target := prediction

[FAIRNESS]: check_at x => CLASSIFICATION.EQUITY()
```

Expected failure:

```text
semantic validation rejects FAIRNESS with pointwise scope if FAIRNESS requires pairwise scope.
```

---

## Golden Sample Roadmap

Each example should eventually become a golden sample with expected artifacts:

| Example | CST | AST | Semantic | IR1 | IR2 | BackendQuery |
|---|---|---|---|---|---|---|
| Minimal Bound Check | planned | planned | planned | planned | planned | planned |
| Bounded Score Range | planned | planned | planned | planned | planned | planned |
| Local Robustness | planned | planned | planned | planned | planned | planned |
| Pairwise Monotonicity | planned | planned | planned | planned | planned | planned |
| Quantified Bound | planned | planned | planned | planned | planned | planned |

---

## Related Documents

- [Syntax](syntax.md)
- [Properties](properties.md)
- [Scopes](scopes.md)
- [Assertions](assertions.md)
- [Golden Samples](../testing/golden-samples.md)
