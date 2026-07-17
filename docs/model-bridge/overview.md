# ModelBridge Overview

> Status: Implemented for sklearn numeric affine regression

ModelBridge connects a real model artifact to backend-neutral constraints without leaking framework-specific objects into the compiler.

## Boundary

```text
model artifact + optional dataset/schema
  → framework detection and introspection
  → ModelSchema
  → requested ModelEvaluation identities from IR2
  → one model constraint per evaluation
```

The bridge does not choose a point from a semantic scope. It receives the exact evaluations requested by the compiled property.

## Schema authority

An explicit schema is authoritative. Otherwise, sklearn `feature_names_in_` is the ordered input contract when available. A dataset supplies compatible dtypes and may also serve as the runtime anchor lookup source, but lookup/provenance columns are not promoted to features.

Preprocessing reconstruction remains outside V1. Anchors and domains are expressed in the transformed feature space consumed by the encoded estimator.

## Per-point affine encoding

For each distinct evaluation `(model, point, target)`, `LinearRegression` emits:

```text
target[point] = intercept + Σ coefficient_i * point.feature_i
```

Coefficients and intercept are shared across evaluations. Input and output symbols remain distinct per point.

The encoder validates that every requested evaluation has exactly one equation and that no duplicate, disconnected, or unrequested equation crosses the boundary.

## Implemented profile

- sklearn `LinearRegression`;
- scalar numeric output;
- numeric transformed features;
- one or more point evaluations of the same model;
- replay through the real estimator `predict(...)`.

## Outside V1

- arbitrary preprocessing pipelines;
- multi-output estimators;
- trees, ensembles, neural networks, and nonlinear model families;
- categorical/tensor model inputs;
- several model artifacts in one property.
