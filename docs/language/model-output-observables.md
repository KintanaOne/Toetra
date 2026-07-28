# Model output observables

> Status: Public and executable since `1.0.0rc2`; current in `1.0.0rc3`
> Scope: Declarative regression and binary-classification output views
> Audience: users, semantic contributors, and model-encoder authors

## Output identity and evaluation

The header declares one output identity:

```toetra
target := decision
```

`target[point]` evaluates that output for one model-input point. The bracket
selects the point, not an output index.

When exactly one eligible point is visible, `target` is shorthand for its
evaluation. Multi-point properties require an explicit index.

## Regression value

The scalar regression observable is the evaluation itself:

```toetra
target[applicant] <= 0.20
```

The public V1 route supports this form for a fitted single-output scikit-learn
`LinearRegression` with finite transformed numeric inputs.

## Predicted label

Classification selects the user-facing label explicitly:

```toetra
target[x0].label == "approved"
```

The literal denotes a model label, not a framework class index. Supported label
comparisons are:

```text
label == literal
label != literal
label == other_label_observable
label != other_label_observable
```

Ordering and arithmetic on labels are semantic errors.

## Class probability estimate

```toetra
target[x0].probability("approved") >= 0.80
```

`probability(label)` denotes the class probability estimate defined by the
recognized model semantic profile. It does not claim statistical calibration.

The public binary route supports order comparisons against thresholds strictly
inside `(0, 1)`. It excludes:

- probability `==` and `!=`;
- thresholds exactly `0` or `1`;
- probability arithmetic;
- probability-to-probability comparisons;
- multiclass probability semantics.

## Native decision threshold and property threshold

The direct binary logistic profile uses:

```text
positive-class probability > 0.5  → positive label
positive-class probability <= 0.5 → negative label
```

The strictness is normative: equality at `0.5` selects the negative label.

A threshold written by the user is a separate property:

```toetra
target[x0].probability("approved") >= 0.80
```

A point can therefore have predicted label `"approved"` while failing the
stronger `0.80` requirement.

## `CLASSIFICATION.EQUAL()`

```toetra
model := "binary.joblib"
target := decision

[ROBUSTNESS]:
forall baseline, candidate
=> CLASSIFICATION.EQUAL() using Z3
```

The predicate is sugar for predicted-label equality across exactly two visible
binary evaluations. Semantic validation rejects any other point count or
incompatible output schema.

## User-facing boundary

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

Reports may expose selected internal quantities as technical lowering evidence.
That evidence does not make them writable source-language expressions.

## Schema-aware validation

Before model lowering, semantic validation checks:

- regression versus classification output kind;
- explicit observable requirement for classification;
- point visibility and unambiguous shorthand;
- label literal type and membership in the model schema;
- allowed ordering, equality, and arithmetic operations;
- exactly two evaluations for `CLASSIFICATION.EQUAL()`.

An unknown label or invalid observable fails before backend execution.

## Public execution boundary

Classification observables are public only for the direct fitted binary
scikit-learn `LogisticRegression` route named in the
[Public V1 profile](../public-v1-profile.md). The route preserves:

- requested observable and label;
- native and property thresholds;
- model semantic profile;
- probability-lowering evidence;
- numeric compatibility and permitted conclusions;
- concrete label, probability, decision-value, and original-property replay.

It does not include multiclass models, calibrated/custom-threshold wrappers, or
sklearn preprocessing pipelines.

## Related pages

- [Language support levels](support-levels.md)
- [Public V1 profile](../public-v1-profile.md)
- [Binary classification profile](../contracts/binary-classification-profile.md)
- [Model output observables contract](../contracts/model-output-observables.md)
- [Assertions](assertions.md)
