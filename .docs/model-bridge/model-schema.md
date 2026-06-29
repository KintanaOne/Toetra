# ModelSchema

> Status: implemented / stabilizing  
> Scope: normalized model representation  
> Priority: P0

## Purpose

`ModelSchema` is the normalized FORML representation of a machine learning model interface.

It acts as the bridge between:

- ML framework objects;
- DSL semantic validation;
- model constraint generation;
- backend lowering.

## Why ModelSchema Exists

A machine learning framework object is not a stable compiler artifact.

FORML needs a representation that is:

- normalized;
- framework-independent;
- serializable in principle;
- usable by semantic validation;
- usable by lowering stages;
- independent from direct framework APIs.

`ModelSchema` provides that boundary.

## Conceptual Structure

```text
ModelSchema
├── framework
├── model_type
├── features
│   ├── feature name
│   ├── dtype
│   └── nullable
├── target
├── task
└── metadata
```

## Current Fields

| Field | Meaning | Status |
|---|---|---|
| `framework` | Detected framework identity. | implemented |
| `model_type` | Runtime model class name. | implemented |
| `features` | Mapping of feature names to `FeatureSchema`. | implemented |
| `target` | Target column or target identifier. | implemented / stabilizing |
| `task` | Classification, regression, or unknown. | implemented / stabilizing |
| `metadata` | Optional framework-specific metadata. | implemented |

## FeatureSchema

Each feature is represented by a `FeatureSchema`.

```text
FeatureSchema
├── name
├── dtype
└── nullable
```

| Field | Meaning |
|---|---|
| `name` | Feature name as used by the model or dataset. |
| `dtype` | FORML semantic data type. |
| `nullable` | Whether missing values are present or allowed. |

## Semantic Type Vocabulary

Feature dtypes should use FORML semantic data types.

Current vocabulary:

| Type | Meaning |
|---|---|
| `INT` | Integer-like feature. |
| `FLOAT` | Floating-point feature. |
| `BOOL` | Boolean feature. |
| `STRING` | String or categorical-like feature. |
| `NoneType` | Null-like value. |

## Role in Semantic Validation

`ModelSchema` allows FORML to move from internal DSL validation to model-aware validation.

Without `ModelSchema`, FORML can resolve that a feature reference belongs to a semantic entity such as `x'`.

With `ModelSchema`, FORML can additionally check whether the feature exists and whether its type is compatible with the logical assertion.

Example:

```text
x'.age <= 30
```

Schema-aware validation should verify:

```text
age exists in ModelSchema.features
age dtype is numeric
<= is compatible with numeric values
```

## Role in Model Constraints

`ModelSchema` is also the source for future model-derived constraints.

Examples:

```text
feature existence
feature dtype
feature nullability
input dimensionality
task compatibility
target compatibility
framework metadata
```

These constraints may later be aggregated with DSL assertions before backend lowering.

## Role in Backend Lowering

Backend lowering should not consume raw framework model objects directly when avoidable.

Instead, the lowering process should consume:

```text
AggregatedAssertionSet + ModelSchema + ModelConstraints
```

This keeps the compiler pipeline independent from framework APIs.

## Invariants

1. `ModelSchema` must be backend-independent.
2. `ModelSchema` must be framework-normalized.
3. Feature names must be stable string keys.
4. Feature dtypes must use FORML semantic vocabulary.
5. Framework-specific metadata must remain optional.
6. Absence of optional metadata must not break generic validation.
7. The schema must be safe to pass across compiler stages.

## Target Guarantees

Target guarantees for the stabilized ModelSchema boundary:

| Guarantee | Meaning |
|---|---|
| Feature completeness | Every model input feature is represented. |
| Target coherence | The target is explicit and compatible with the declared task. |
| Type coherence | All features have normalized semantic dtypes. |
| Metadata isolation | Framework-specific details do not leak into generic compiler stages. |
| Backend readiness | The schema contains enough information to support model constraints and lowering. |

## Open Questions

- Should `target` be mandatory or inferred only in development mode?
- Should categorical domains be represented in `FeatureSchema`?
- Should feature bounds be represented directly in the schema?
- Should metadata be split into `runtime_metadata` and `verification_metadata`?
- Should the schema become serializable as a standalone FORML artifact?
