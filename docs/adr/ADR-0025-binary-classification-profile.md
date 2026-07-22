# ADR-0025 — Define the Initial Binary Classification Profile

> Status: Accepted — public in `1.0.0rc2`
> Date: 2026-07-20
> Scope: binary classification semantics, initial ModelBridge route, DSL observables, decision boundary, exclusions

## Context

FORML needs an initial classification route that is useful to users while
remaining small enough to specify, verify, report, replay, and stabilize before a
new release candidate.

`sklearn.linear_model.LogisticRegression` is a strong first concrete estimator
because its binary decision semantics can be represented through an affine latent
quantity. However, FORML must not define classification as "whatever sklearn
returns" or expose sklearn method names in the DSL.

The initial profile must also distinguish:

- the model's native **decision threshold**, which determines `predict`;
- a user-defined **property threshold**, such as a required probability of
  `0.80`.

## Decision

FORML will define a framework-neutral **binary logistic affine classification
profile**. A direct fitted binary scikit-learn `LogisticRegression` will be the
first concrete ModelBridge route implementing that profile.

### Public DSL observables

The initial target syntax is:

```text
target[x0].label == "approved"
target[x0].probability("approved") >= 0.80
```

The user may refer to labels and class probability estimates. The user may not
refer directly to:

- a logit;
- a decision function;
- a latent score or generic `score`;
- `predict`, `predict_proba`, or `classes_`;
- an affine equation;
- Z3 symbols.

Those are implementation or evidence concepts, not public specification
constructs.

### Model-family semantics

For the profile, the bridge materializes an oriented latent decision value:

```text
z(x) = w · x + b
```

The symbol and orientation are internal. The public meaning is defined by the
resolved labels and the native decision policy.

### Native decision policy

The initial profile supports the estimator's standard binary decision policy:

| Condition | Predicted label |
|---|---|
| positive-class probability `> 0.5` | positive label |
| positive-class probability `<= 0.5` | negative label |
| oriented decision value `> 0` | positive label |
| oriented decision value `<= 0` | negative label |

The equality boundary therefore belongs to the negative label.

The value `0.5` is not read from a learned `threshold_` attribute on a direct
`LogisticRegression`. It is part of the recognized semantic profile of that
estimator type. FORML records the policy used rather than pretending it was a
learned model parameter.

### Pairwise predicted-label relations

The profile supports `target[left].label == target[right].label` and `!=`. Equality means the two oriented decision quantities lie in the same native decision region; inequality means opposite regions. `CLASSIFICATION.EQUAL()` is sugar for equality, requires exactly two visible input points, and is lowered before NNF rather than interpreted by a backend.

### Property thresholds

A probability in the user's property is independent from the native decision
threshold:

```text
target[x0].probability("approved") >= 0.80
```

A model can predict `"approved"` while failing that stronger property.

Probability-order properties may be lowered through the monotonic logistic link.
The algebraic transformation and its numerical materialization must be recorded
and qualified under ADR-0018 and ADR-0024. P21.8.1 requires certified outward
bounds built from independent intervals for `ln(p)` and `ln(1 - p)`; a rounded
odds ratio is not a valid intermediate for proof-grade threshold materialization.

### Supported initial estimator route

The first concrete route accepts:

- a direct fitted `sklearn.linear_model.LogisticRegression`;
- exactly two classes;
- one output;
- finite numeric transformed inputs;
- finite coefficients and intercept;
- labels with a deterministic canonical representation supported by the schema;
- the native standard decision policy described above.

### Explicitly unsupported initial routes

The first profile rejects, with structured ModelBridge diagnostics:

- multiclass logistic regression;
- `FixedThresholdClassifier`;
- `TunedThresholdClassifierCV`;
- `CalibratedClassifierCV`;
- sklearn `Pipeline` and preprocessing reconstruction;
- wrappers that replace or customize `predict`;
- custom decision thresholds;
- arbitrary Python object labels;
- classifiers without the declared probability observable;
- multi-output classification.

These are not impossible future features. They require distinct semantic
profiles and evidence contracts.

### Initial expression restrictions

The first executable profile will prioritize:

- label equality and inequality against a literal label;
- probability order comparisons against a threshold strictly between zero and
  one;
- explicit equality of labels between two points after the one-point route is
  stable.

Initially deferred:

- exact probability equality or inequality;
- probability thresholds at exactly zero or one;
- general arithmetic over probabilities;
- public access to latent quantities;
- multiclass relations, top-k, abstention, or ranking semantics.

### Release rule

ADR-0022 and the `1.0.0rc1` public profile remain authoritative until the whole
classification route passes its documentation, compiler, ModelBridge, backend,
reporting, replay, packaging, and clean-install gates.

Only the final hardening patch may amend the public V1 profile and prepare
`1.0.0rc2`. P21.11 has now satisfied that gate; ADR-0026 adopts this profile in
the public release candidate.

## Rationale

The route provides immediate user value for common classification properties
without widening the initial proof surface to every sklearn classifier or every
possible decision policy.

The framework-neutral profile also permits another framework to implement the
same mathematical contract without changing the DSL.

## Consequences

- Label order and orientation are resolved by the bridge, never written by the
  user as `class[0]` or `class[1]`.
- The strict boundary at zero must be represented and tested exactly.
- Probability thresholds require explicit numeric compatibility evidence.
- ModelBridge routing must reject wrappers before backend execution.
- Reporting must distinguish native decision threshold from property threshold.

## Alternatives considered

### Support only predicted labels

Rejected because probability requirements are a core user need and can be
supported through an auditable lowering for this model family.

### Expose the logit to avoid probability lowering

Rejected because it transfers implementation complexity to users and makes the
language model-centric rather than intention-centric.

### Introspect any classifier with `predict_proba`

Rejected because shared method names do not imply shared decision thresholds,
calibration meaning, wrapper behavior, or verification encodings.

### Support custom thresholds immediately

Rejected because threshold wrappers introduce a separate decision-policy
contract. They should be added after the native route is stable.

## Impact on FORML

This ADR defined the target scope for Patch 21. The complete route is now
implemented and adopted by ADR-0026 in `1.0.0rc2`; ADR-0022 remains the historical
`1.0.0rc1` freeze.

## P21.9 reporting and replay implementation

The initial profile now has a complete evidence route for concrete assignments:

- formal label reconstruction with the strict zero-boundary policy;
- reconstructed binary probabilities identified as approximate presentation
  evidence;
- latent decision value retained as auxiliary technical evidence;
- native and property thresholds reported separately;
- concrete sklearn observation through `predict`, `predict_proba`, and
  `decision_function` behind a generic observer protocol;
- exact label comparison, tolerance-based numeric comparison, and concrete
  reevaluation of the original user property.

This completed the P21.9 gates. Public adoption is recorded separately by
ADR-0026 after the remaining pairwise and release gates passed.


## P21.10 pairwise implementation

Explicit label equality and inequality execute end to end, preserve the
zero-to-negative boundary rule, carry both evaluations in lowering evidence, and
appear as pairwise evidence in reports.

## P21.11 public adoption

ADR-0026 adopts this complete profile in `1.0.0rc2` after documentation,
compiler, ModelBridge, backend, numeric, reporting, replay, packaging, and
clean-install gates were added to the release contract.
