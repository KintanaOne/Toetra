# ModelBridge overview

> **Status:** Implemented for the public sklearn affine routes
>
> **Scope:** model artifacts, schema, formal encoding, and replay observation

ModelBridge prevents framework-specific estimators from leaking into compiler
IR. It provides four related but distinct services.

## Services

| Service | Output | Consumer |
|---|---|---|
| load/detect/introspect | `ModelSchema` plus optional concrete model | semantic validation and runtime |
| model-family semantics | lowered IR1 task plus evidence | NNF/IR2 |
| formal encoder | model `AssumptionIR2` values | IR2 builder |
| runtime observer | concrete `ModelObservation` | replay |

## Artifact path

```text
model artifact + optional dataset + target
→ loader
→ framework detector
→ introspector
→ ModelSchema
```

`verify(...)` can instead receive an explicit normalized schema. The two paths
are mutually exclusive to preserve one metadata authority.

`ModelSchema` carries ordered features, output name/type, framework, task,
model family, and output profile. It is used while validating feature names,
types, target references, and output observables.

## Model-semantic path

Public classification observables require model-family meaning:

```text
IR1 public observable + ModelSchema
→ semantic profile
→ canonical model-quantity constraint + lowering evidence
```

The direct binary-logistic profile uses an internal oriented decision value.
That quantity never becomes DSL syntax or a public model output.

## Formal-encoding path

The compiler discovers exact model-evaluation identities from the lowered
property. The encoder factory receives those identities and emits one equation
per requested `(model, point, output)`:

```text
ModelSchema + requested evaluations
→ affine AssumptionIR2 values
```

Regression encodes `target[point] = intercept + Σ weightᵢ·featureᵢ`.
Binary logistic regression encodes the corresponding oriented decision
quantity. Coefficients are shared, but symbols remain distinct per point.

## Replay path

A framework-neutral runtime-observer registry executes the retained concrete
model after formal verification. The sklearn observer normalizes:

- `predict` for scalar regression or predicted labels;
- `predict_proba` for label-keyed probabilities;
- `decision_function` for the binary logistic technical quantity.

Replay does not participate in backend proof or route selection.

## Implemented public profile

- fitted single-output sklearn `LinearRegression`;
- direct fitted binary sklearn `LogisticRegression`;
- finite numeric transformed features;
- one output;
- one or more exact point evaluations;
- Z3 execution;
- point-aware reporting and concrete replay.

## Boundaries outside V1

- preprocessing reconstruction;
- multiclass and multi-output models;
- wrappers, calibrators, or custom decision thresholds;
- trees, ensembles, neural networks, and nonlinear encoders;
- categorical/tensor symbolic inputs;
- several model artifacts in one property.

Internal detection or introspection code for another framework is not an
end-to-end support claim. See
[supported frameworks](supported-frameworks.md) and the
[public V1 profile](../public-v1-profile.md).
