# Model Output Observables

> Status: P21.2 syntax and AST implemented — semantic execution pending
> Scope: declarative references to regression and classification outputs

## Purpose

Toetra properties describe what must hold for a model output. They do not call
framework methods and do not expose backend variables.

The `target` keyword names the output port declared by the specification header.
An observable selects the user-relevant value of that output at a point.

## Scalar regression

The existing scalar regression form remains unchanged:

```text
target[x0] <= 0.20
```

When exactly one point is eligible, the short form remains valid:

```text
target <= 0.20
```

## Predicted label

A classification property selects the predicted label explicitly:

```text
target[x0].label == "approved"
```

The label is written as the domain value known to the model schema. Users do not
refer to a class index or to the internal order of framework classes.

## Class probability estimate

A classification property may select the probability estimate associated with a
named label:

```text
target[x0].probability("approved") >= 0.80
```

The word `probability` means the class probability estimate exposed by the model
semantic profile. It does not assert that the estimator is statistically
calibrated.

## Native decision threshold versus property threshold

The initial binary logistic profile uses its native decision policy:

```text
positive-class probability > 0.5  → positive label
positive-class probability <= 0.5 → negative label
```

A threshold written in a property is a separate requirement:

```text
target[x0].probability("approved") >= 0.80
```

A point may therefore have label `"approved"` while violating the stronger
probability requirement.

## User-facing vocabulary boundary

The following concepts are intentionally not DSL observables:

```text
logit
decision_function
predict
predict_proba
classes_
score
latent score
Z3 symbol
```

Toetra may explain internal transformations involving such concepts in technical
evidence, but users specify labels and probabilities.

## Point rules

Output observables follow the existing point-binding contract:

```text
target[x0].label
target[x1].probability("approved")
```

The point may be omitted only when exactly one eligible default point exists:

```text
target.label == "approved"
target.probability("approved") >= 0.80
```

No multi-point property receives an implicit point selection.

## Target initial comparison profile

| Observable | Initial comparisons |
|---|---|
| predicted label against a literal | `==`, `!=` |
| class probability against a threshold in `(0, 1)` | `<`, `<=`, `>`, `>=` |
| predicted label between two points | `==`, `!=`, after the one-point route is stable |

Initially deferred:

- ordering comparisons on labels;
- probability equality and inequality;
- probability thresholds exactly zero or one;
- arithmetic over probabilities;
- direct access to internal decision values;
- multiclass-specific relations.

## Diagnostics

A classification output referenced without an observable must produce a targeted
diagnostic such as:

```text
A classification output requires an explicit observable:
target[x0].label or target[x0].probability(label).
```

An unknown label must be rejected at semantic validation, before ModelBridge or
backend execution.

## Current implementation status

These forms are public and executable in `1.0.0rc2` for the direct fitted binary
sklearn `LogisticRegression` profile. Binding validates labels and capabilities,
IR1 preserves the declarative observable, model-semantic lowering creates
auditable internal constraints, Z3 executes the route, and reports/replay
reconstruct the user-facing label and probabilities.
