# Public V1 profile

> Release candidate: `1.0.0rc2`  
> Contract date: 2026-07-22

This page is the public source of truth for executable Toetra V1 support.

## Supported end-to-end routes

| Axis | Regression route | Binary-classification route |
|---|---|---|
| Python | 3.11 and 3.12 | 3.11 and 3.12 |
| Framework | scikit-learn | scikit-learn |
| Model | fitted single-output `LinearRegression` | direct fitted binary `LogisticRegression` |
| Inputs | finite transformed numeric features | finite transformed numeric features |
| Output | one numeric regression value | one predicted label plus class probabilities |
| Public DSL | scalar `target[point]` | `target[point].label`, `target[point].probability(label)` |
| Encoding | affine output equation | affine oriented-decision equation |
| Backend | Z3 | Z3 |
| Reports | text, HTML, Jupyter, records/DataFrame, JSON v6 | same plus additive model-evaluation evidence |
| Replay | concrete regression output | label, probabilities, decision value, original property |

Both routes support homogeneous `forall` or `exists` bindings, points/anchors,
numeric domains, affine arithmetic, Boolean logic, and `PROVED`,
`COUNTEREXAMPLE`, `WITNESS`, `NO_WITNESS`, or `UNKNOWN`.

## Binary-classification semantics

```toetra
model := "binary.joblib"
target := decision

[LOGIC]:
forall applicant
with domain(applicant.income: [3.0, 6.0])
=> target[applicant].probability("yes") >= 0.80 using Z3
```

The DSL does not expose the logit, `decision_function`, `predict_proba`, class
indices, sklearn internals, or Z3 symbols.

The direct binary logistic route uses:

```text
positive-class probability > 0.5  → positive label
positive-class probability <= 0.5 → negative label
```

A user threshold is a distinct property threshold. Order comparisons are
supported for thresholds strictly inside `(0, 1)`. Pairwise label equality and
inequality are supported; `CLASSIFICATION.EQUAL()` requires exactly two distinct
visible evaluations.

## Numeric meaning

The built-in routes reason over exact-real affine abstractions extracted from
framework floating-point state. Reports preserve numeric compatibility,
semantic-lowering evidence, provenance, and concrete replay rather than claiming
bit-exact global sklearn equivalence.

## Explicit exclusions

- multiclass and multi-output classification;
- trees, ensembles, neural networks, and nonlinear encoders;
- sklearn `Pipeline` and symbolic preprocessing reconstruction;
- `FixedThresholdClassifier`, `TunedThresholdClassifierCV`,
  `CalibratedClassifierCV`, custom wrappers, and custom thresholds;
- probability equality/inequality, thresholds `0` or `1`, and probability
  arithmetic;
- categorical/string backend reasoning, alternating quantifiers, and built-in
  backends other than Z3.

## Extension rule

A new route is public only when schema, semantics, encoder, capabilities, numeric
compatibility, execution, reports, replay, and unit/contract/end-to-end/
clean-install/release tests agree.
