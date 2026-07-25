# ADR-0008 — Use ModelSchema as the Bridge Between Models and Toetra

> Status: Accepted  
> Date: 2026-06  
> Scope: ModelBridge

> **Patch 21 target amendment:** ADR-0023 replaces the assumption that the selected `target` is always one directly addressable scalar value. The current `1.0.0rc1` implementation remains governed by this ADR, while typed output ports and observables are the accepted target for `1.0.0rc2`.

## Context

Toetra properties refer to model-facing concepts such as features, targets, task types, and model behavior.

The DSL alone cannot know whether:

- a referenced feature exists,
- a target column is valid,
- a model is a classifier or regressor,
- a backend can represent the model,
- a property is compatible with the model.

## Decision

Toetra introduces ModelBridge and uses `ModelSchema` as the normalized bridge between ML models and the Toetra compiler.

The ModelBridge pipeline is:

```text
model artifact
→ loader
→ loaded model
→ framework detection
→ introspector
→ ModelSchema
```

## Rationale

The compiler should not depend directly on sklearn, XGBoost, PyTorch, TensorFlow, or serialization formats.

Instead, all framework-specific details should be normalized into a common schema.

## Consequences

### Positive

- Semantic validation can become model-aware.
- Backend lowering can rely on normalized metadata.
- New frameworks can be added behind the ModelBridge boundary.
- The compiler remains independent from model serialization details.

### Negative

- ModelBridge must handle incomplete metadata.
- Some models may require dataset/schema input for feature detection.
- Framework-specific introspection can be fragile.

## Alternatives considered

### Let each backend inspect the model directly

Rejected because it duplicates model introspection and couples backends to ML frameworks.

### Let the DSL manually declare all model metadata

Rejected because it would be error-prone and burdensome for users.

## Impact on Toetra

ModelSchema is a P0 architectural object.

It is required for schema-aware semantic validation and future model constraint generation.
