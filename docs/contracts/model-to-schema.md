# Model to Schema Contract

> Status: P0 / Partially Implemented  
> Scope: Serialized model artifact to normalized ModelSchema  
> Implementation: loaders, detector, sklearn/XGBoost introspectors  
> Audience: ModelBridge maintainers, semantic maintainers, backend authors

## Purpose

The Model to Schema contract defines how FORML converts a model artifact into a normalized representation usable by the compiler.

It answers the question:

```text
What does FORML know about the model it is verifying?
```

ModelBridge is the subsystem responsible for this contract.

---

## Input

```text
Model artifact
```

Potential input artifacts:

- `.pkl` model;
- `.joblib` model;
- future JSON/model metadata artifacts;
- optional dataset path;
- optional external schema.

---

## Output

```text
ModelSchema
```

A `ModelSchema` contains:

- framework identity;
- model type;
- feature schema;
- target name;
- task type;
- framework-specific metadata.

---

## ModelBridge Pipeline

```text
model path
    ↓
LoaderFactory
    ↓
loaded model
    ↓
ModelDetector
    ↓
framework
    ↓
IntrospectorFactory
    ↓
framework-specific introspector
    ↓
ModelSchema
```

---

## Current Supported Frameworks

| Framework | Status | Notes |
|---|---|---|
| scikit-learn | Implemented / stabilizing | Detection and introspection exist. |
| XGBoost | Implemented / stabilizing | Reuses sklearn-style introspection and enriches metadata. |
| PyTorch | Planned | Framework enum exists, introspector not yet implemented. |
| TensorFlow | Planned | Framework enum exists, introspector not yet implemented. |

---

## Guarantees

If schema construction succeeds:

- the model artifact was loadable;
- the framework was detected;
- an introspector was selected;
- features are available through `ModelSchema.features`;
- target and task are available;
- downstream semantic validation can reason about feature existence and dtype;
- future model constraint generation can use the schema as input.

---

## Non-Goals

The Model to Schema contract does not:

- prove model correctness;
- encode the model into a solver;
- execute predictions;
- verify FORML properties;
- choose the verification backend.

---

## Failure Modes

Expected failures include:

- unsupported model file extension;
- missing file;
- deserialization failure;
- unsupported framework;
- missing feature metadata;
- unsupported introspector;
- inconsistent external schema.

---

## Stabilization Notes

The contract should stabilize:

- loader error naming and hierarchy;
- dataset requirement for feature inference;
- model task normalization;
- target inference policy;
- schema override policy;
- framework enum consistency.

---

## Miova Hooks

Miova may mutate model/schema artifacts by:

- removing a feature;
- changing a dtype;
- corrupting framework metadata;
- changing task type;
- removing target;
- altering feature nullability;
- generating unsupported model metadata.

Expected outcome:

```text
Invalid schema mutation → schema or semantic rejection
Valid schema mutation   → semantic integration may continue
```

## Patch 21 Typed Output Addendum

Patch 21 replaces the loose scalar-target assumption with the accepted
[Model Output Observables Contract](model-output-observables.md).

The P21.1 `ModelSchema` now exposes `output_name` plus a typed
`output_schema`. The normalized schema contains:

- output-port identity;
- task kind;
- available public observables;
- observable scalar types;
- canonical labels for classification;
- the model semantic profile needed for lowering.

Free-form metadata such as `classes` remains source material for an
introspector, but it is not itself the normalized output contract. `target`,
`target_dtype`, and `target_source_dtype` are temporary read-only projections from
the typed output schema while internal consumers migrate.
