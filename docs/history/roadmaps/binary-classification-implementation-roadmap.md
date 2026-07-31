# Binary classification

> **Status:** Delivered in `1.0.0rc2` on 2026-07-22

The second public model route extended Toetra from scalar regression outputs to
typed binary-classification observables without exposing framework-specific
scores in the language.

## Typed model outputs

Model schemas learned to distinguish regression and classification outputs.
The language added two public observables:

- `target[point].label` for the predicted class;
- `target[point].probability(label)` for the probability of a declared class.

Semantic validation bound each observable to a model output, point, scalar
type, and canonical label. IR1 retained both the shared model evaluation and
the selected observable.

## Framework-neutral semantics

Predicted-label and probability-order properties were lowered through a
framework-neutral semantic layer. The exact native decision boundary was
preserved, and non-exact probability thresholds used certified directed logit
intervals rather than silently rounded host values.

The first concrete bridge supported direct fitted binary sklearn
`LogisticRegression`. Threshold wrappers, calibration wrappers, multiclass
models, probability equality, probability arithmetic, and top-k behavior
remained outside the public profile.

## Execution, evidence, and adoption

Z3 executed label and probability-threshold relations, including pairwise label
equality and inequality. Reports preserved the source observable, internal
lowering evidence, and per-point model evaluations. Replay compared witnesses
and counterexamples with the real classifier using tolerance-aware three-valued
evaluation.

Clean-install demonstrations, contract tests, golden reports, and release
documentation completed public adoption in `1.0.0rc2`. The normative boundary
is recorded in the
[binary-classification profile](../../contracts/binary-classification-profile.md)
and its [test matrix](../../testing/binary-classification-test-matrix.md).
