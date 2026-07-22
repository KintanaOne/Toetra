# Initial Binary Classification Profile Contract

> Status: Implemented — public in `1.0.0rc2`
> Normative ADR: [ADR-0025](../adr/ADR-0025-binary-classification-profile.md)
> Scope: binary logistic affine semantics and first sklearn route

## Purpose

This contract freezes the first classification behavior FORML will implement. It
is intentionally narrower than the general classification vocabulary.

## Framework-neutral profile

Stable semantic profile identifier:

```text
forml.binary_logistic_affine_classifier
```

The identifier describes a mathematical and decision-semantic family, not a
Python estimator class.

## First concrete route

| Axis | Initial accepted value |
|---|---|
| Framework | scikit-learn |
| Estimator | direct fitted `sklearn.linear_model.LogisticRegression` |
| Task | binary classification |
| Outputs | one classification output |
| Inputs | finite transformed numeric features |
| Labels | two deterministic canonical scalar labels |
| Public observables | predicted label and class probability estimate |
| Native decision threshold | positive probability strictly greater than `0.5` |
| Equivalent latent boundary | oriented decision value strictly greater than `0` |
| Equality boundary | negative label |
| First backend route | Z3 after canonical affine lowering |

## Native decision policy

Let `positive_label` and `negative_label` be resolved by the bridge. Let `z(x)`
be the internal oriented decision value.

```text
predicted_label(x) = positive_label  iff z(x) > 0
predicted_label(x) = negative_label  iff z(x) <= 0
```

Equivalently for the positive-class probability estimate:

```text
predicted_label(x) = positive_label  iff p(x) > 0.5
predicted_label(x) = negative_label  iff p(x) <= 0.5
```

The strictness is normative. A point exactly on the boundary belongs to the
negative label.

## Threshold provenance

For a direct `LogisticRegression`, the native `0.5` threshold is supplied by the
recognized semantic profile. It is not asserted to be a learned attribute read
from the fitted object.

A wrapper with an explicit or tuned threshold does not satisfy this contract and
must route to a future distinct profile.

## Public property forms

Target forms to be implemented:

```text
target[x0].label == "approved"
target[x0].label != "approved"
target[x0].probability("approved") >= 0.80
target[x0].probability("approved") < 0.20
target[x0].label == target[x1].label
target[x0].label != target[x1].label
```

A property threshold such as `0.80` is independent from the native decision
threshold `0.5`.

## Pairwise predicted-label relations

For two distinct model evaluations with oriented decision values `z0` and `z1`, equality is exact:

```text
(z0 > 0 and z1 > 0) or (z0 <= 0 and z1 <= 0)
```

Inequality is also exact:

```text
(z0 > 0 and z1 <= 0) or (z0 <= 0 and z1 > 0)
```

The non-strict negative branch preserves the rule that exact zero belongs to the negative label. `CLASSIFICATION.EQUAL()` is sugar for explicit predicted-label equality and requires exactly two visible model-input points.

## Probability-lowering contract

For a valid threshold `p` strictly between zero and one, order comparisons may be
rewritten through the monotonic logistic link. The public contract requires:

- correct orientation for either requested label;
- exact handling of `p = 0.5`;
- qualified numeric materialization for other thresholds;
- preservation of strict versus non-strict operators;
- lowering evidence containing the source probability threshold;
- no public exposure requirement for the latent decision value.

Initially unsupported:

- probability `==` and `!=`;
- thresholds exactly `0` or `1`;
- arithmetic between probabilities;
- probability comparisons between two evaluations.

### Implemented numeric materialization

P21.8 materializes non-native thresholds without silently inserting a host
binary float:

1. parse and preserve the original DSL decimal spelling;
2. evaluate `logit(p)` as `ln(p) - ln(1 - p)`;
3. enclose both logarithms independently at working precision;
4. subtract their intervals with directed rounding;
5. round the result outward to 50 published significant digits, using at least
   20 guard digits internally and expanding working precision for long literals;
6. orient the interval for the selected label;
7. choose a directed bound according to comparison direction and logical
   polarity;
8. record the exact expression, both bounds, selected side, published precision,
   working precision, guard digits, compatibility class, and permitted
   conclusions;
9. identify the corrected materialization as probability transformation version
   `2`.

The implementation must not compute a rounded odds ratio first and then enclose
its logarithm. That procedure does not certify an interval around the exact
source-decimal logit.

For non-exact thresholds, the resulting property is a sound
under-approximation of the source property's satisfying set. Universal proofs
and existential witnesses are accepted. Universal counterexamples and
existential no-witness conclusions require future refinement or replay and are
currently reported as `UNKNOWN`.

## Model acceptance preconditions

The bridge must validate before encoding:

- fitted estimator state;
- exactly two classes;
- exactly one coefficient row;
- coefficient width matching the feature schema;
- one compatible intercept;
- finite coefficients and intercept;
- deterministic supported labels;
- absence of an unsupported wrapper or preprocessing container.

## Structured rejection cases

The bridge must reject before backend execution:

| Case | Reason |
|---|---|
| multiclass estimator | decision and probability lowering profile differs |
| unfitted estimator | no stable learned equation |
| `FixedThresholdClassifier` | custom threshold policy |
| `TunedThresholdClassifierCV` | learned wrapper threshold policy |
| `CalibratedClassifierCV` | different probability semantics |
| sklearn `Pipeline` | symbolic preprocessing outside initial scope |
| custom wrapper | decision policy not recognized |
| non-finite coefficients | incompatible numeric source |
| arbitrary object labels | no deterministic canonical label contract |

## Reporting requirements

A classification result must be able to report separately:

- requested observable and label;
- native decision threshold;
- property threshold, when present;
- model semantic profile;
- lowering transformation;
- internal decision value as technical evidence;
- reconstructed class probabilities;
- predicted label;
- margin relative to the requested property;
- numeric compatibility and permitted conclusion.

The internal decision value must never be mislabeled as the public output.

## Replay requirements

Concrete replay must compare the relevant views independently:

- label by exact equality;
- probability by declared numeric tolerance and compatibility policy;
- internal decision value by declared numeric tolerance;
- original property by concrete reevaluation.

The generic replay layer must use a model-observer protocol rather than checking
for a concrete sklearn estimator type directly.

## Explicit non-goals

- multiclass classification;
- custom or tuned thresholds;
- calibrated wrappers;
- preprocessing reconstruction;
- class weights as a separate semantic feature beyond their learned coefficients;
- top-k, abstention, ranking, or cost-sensitive policy semantics;
- public logit or score syntax;
- non-Z3 built-in execution in the initial patch sequence.

## Release gate

This contract remains an accepted target until all `BC-*` acceptance groups in
the [Binary Classification Test Matrix](../testing/binary-classification-test-matrix.md)
are green. Only then may the public V1 profile be amended for `1.0.0rc2`.
