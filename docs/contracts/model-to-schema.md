# Model-to-schema contract

> **Status:** Implemented for the public sklearn routes
>
> **Scope:** model artifact and optional dataset to normalized `ModelSchema`
>
> **Audience:** ModelBridge, semantic, compatibility, and encoder maintainers

This contract defines what downstream stages may rely on after Toetra loads,
detects, and introspects a model.

## Input

The normal public path receives:

- a supported serialized model artifact;
- an optional reference dataset used for feature names, dtypes, and anchor
  lookup;
- the output name selected by the specification/runtime.

An explicit schema is an advanced development input. It is mutually exclusive
with model-artifact introspection so that one metadata authority owns the
verification session.

## Output

Successful construction returns a normalized `ModelSchema` containing:

- framework and concrete model type;
- ordered feature schemas;
- output-port name and task;
- typed regression, classification, or unknown output schema;
- available public observables and their semantic types;
- optional framework/model compatibility descriptor;
- adapter-specific metadata that does not override normalized fields.

The returned schema is a deeply immutable snapshot. Ordered features and
metadata are stored as tuples; nested framework/caller mappings and sequences
are detached and recursively frozen before the constructor succeeds.

`target`, `target_dtype`, and `target_source_dtype` are read-only internal
compatibility projections from the typed output source of truth.

## Implemented pipeline

```text
model path
→ LoaderFactory
→ loaded model
→ ModelDetector
→ IntrospectorFactory
→ ModelSchema
```

Schema construction is separate from:

```text
model-family semantic lowering
formal model encoding
backend routing and execution
runtime observation and replay
```

## Route status

| Framework/model | Schema infrastructure | Public end-to-end route |
|---|---:|---:|
| sklearn single-output `LinearRegression` | implemented | yes |
| direct binary sklearn `LogisticRegression` | implemented | yes |
| other sklearn estimators or wrappers | partial/generic introspection may exist | no |
| XGBoost | internal detection/introspection infrastructure | no |
| PyTorch, TensorFlow, ONNX | no complete built-in schema route | no |

Infrastructure presence never widens the
[public V1 profile](../public-v1-profile.md).

## Guarantees

If schema construction succeeds:

1. the artifact was loaded and its framework detected;
2. a compatible introspector produced normalized feature identities and types;
3. the output name is non-empty and agrees with the typed output schema;
4. task and output kind are coherent;
5. classification labels and observables are structurally valid;
6. downstream semantic validation can check feature and observable references;
7. compatibility evidence, when present, is explicit and backend-independent.
8. no caller- or framework-owned mutable collection can change the normalized
   schema after construction.

These guarantees do not imply that a complete encoder/backend route exists.
Route qualification must still fail closed.

## Failure ownership

Expected failures include:

- missing or unsupported artifact paths;
- deserialization failure;
- unknown framework or missing introspector;
- absent or inconsistent feature metadata;
- invalid output selection;
- task/output-schema conflict;
- invalid or non-finite classification labels;
- ambiguous simultaneous model and schema authorities.

P26 may normalize the public presentation of these failures without weakening
their owning boundary.

## Non-goals

This contract does not:

- prove model correctness;
- reconstruct preprocessing;
- translate model equations into a backend;
- execute predictions or replay;
- choose a backend;
- declare a route public merely because introspection succeeds.

## Patch 21 Typed Output Addendum

The typed output contract separates an output port from its observables.
Regression exposes one scalar value. Classification exposes a label and,
when supported by the recognized model profile, label-keyed probabilities.
Logits, decision functions, class indices, framework methods, and solver
symbols remain internal.

See the [as-built ModelSchema](../model-bridge/model-schema.md),
[model output observables](model-output-observables.md), and
[model semantic lowering](model-semantic-lowering.md).
