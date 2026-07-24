# ADR-0026 — Extend the Public V1 Profile with Binary Classification

> Status: Accepted
> Date: 2026-07-22
> Release: `1.0.0rc2`
> Scope: public V1 profile, binary classification, compatibility, release gates

## Context

ADR-0022 froze the first executable V1 profile around sklearn
`LinearRegression`. Patch 21 subsequently introduced typed output ports,
declarative output observables, model-family semantic lowering, a direct binary
logistic bridge, Z3 execution, reporting, replay, and pairwise label relations.

The route now crosses every required boundary:

```text
DSL → semantic binding → IR1 → semantic lowering → IR2
→ ModelBridge → numeric compatibility → Z3 → report → concrete replay
```

## Decision

FORML `1.0.0rc2` adds one public binary-classification route:

- direct fitted binary `sklearn.linear_model.LogisticRegression`;
- finite transformed numeric features and one output;
- `target[point].label` and `target[point].probability(label)`;
- native positive-label policy `p > 0.5`, equivalently oriented decision value
  `> 0`, with equality assigned to the negative label;
- probability order comparisons for thresholds strictly inside `(0, 1)` using
  certified directed logit intervals;
- explicit pairwise label equality/inequality and `CLASSIFICATION.EQUAL()` for
  exactly two distinct visible evaluations;
- Z3 execution, additive JSON v5 evidence, text/HTML/Jupyter rendering, and
  concrete sklearn replay.

The public `LinearRegression` route remains unchanged.

## Compatibility

JSON report schema v5 remains frozen. Classification evidence is optional and
additive; existing fields are not reinterpreted.

Historical `target`, `target_dtype`, `target_source_dtype`, and `target_name`
projections remain read-only compatibility aliases for the 1.x line. New code
must use output-oriented names. Removal requires a later major version.

## Explicit exclusions

- multiclass and multi-output classification;
- sklearn pipelines and symbolic preprocessing reconstruction;
- threshold, tuning, calibration, and custom prediction wrappers;
- custom decision thresholds;
- probability equality/inequality, thresholds zero or one, and probability
  arithmetic;
- top-k, abstention, ranking, and multiclass relations;
- built-in backends other than Z3.

## Numeric meaning

Framework floating-point parameters are extracted into exact-real affine
abstractions. Non-exact probability thresholds use certified directed intervals
around `logit(p)` and conclusion policies prevent an approximation from yielding
a stronger result than justified. Replay is concrete evidence at returned
assignments, not a global IEEE-754 proof.

## Consequences

- `1.0.0rc2` is a broader release candidate, not a GA declaration.
- Public docs and clean-install probes exercise both model families.
- Unsupported classifier wrappers fail before backend execution.
- Latent model quantities remain internal to lowering and technical evidence.
- ADR-0022 remains the historical `rc1` freeze and is amended by this ADR.

## Release gate

```bash
make ci
make release-check
make review-bundle-check
git diff --check
```
