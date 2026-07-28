# ModelSchema

> **Status:** As built for `1.0.0rc3`
>
> **Scope:** private normalized model boundary used by semantic validation,
> formal encoding, compatibility routing, and replay

`ModelSchema` separates compiler logic from framework objects. A loader and
introspector may inspect sklearn state, but downstream stages receive normalized
feature, output, task, and compatibility information.

## Implemented structure

| Field | Type shape | Meaning |
|---|---|---|
| `framework` | `EnumModelFramework` | detected framework identity |
| `model_type` | `str` | concrete estimator class name |
| `features` | `dict[str, FeatureSchema]` | ordered normalized inputs |
| `output_name` | `str` | selected output-port name |
| `task` | `str` | regression, classification, or unknown task |
| `output_schema` | `ModelOutputSchema` | typed output and available observables |
| `metadata` | `dict[str, Any]` | optional adapter-specific evidence |
| `compatibility` | descriptor or `None` | framework/model numeric contract used by routing |

The concise `output` property returns `output_schema`.

## Feature schema

Each `FeatureSchema` records:

| Field | Meaning |
|---|---|
| `name` | stable feature name |
| `dtype` | normalized Toetra semantic datatype |
| `nullable` | whether the feature permits missing values |
| `source_dtype` | optional original framework/dataset dtype |

Semantic validation uses this information to reject unknown features and
type-incompatible expressions before model encoding or backend execution.

## Typed outputs

`ModelOutputSchema` has three implemented variants:

| Variant | Public observables |
|---|---|
| `RegressionOutputSchema` | one scalar regression value |
| `ClassificationOutputSchema` | predicted label and, when available, class probability |
| `UnknownOutputSchema` | no public observable |

The binary classification schema preserves canonical negative/positive label
orientation and a recognized decision policy. The initial logistic profile uses
strict positive probability `> 0.5`; equality belongs to the negative label.
That policy is model-family meaning, not free-form metadata.

## Pipeline ownership

```text
model artifact + optional dataset
→ loader → detector → introspector
→ ModelSchema
→ semantic validation
→ model-family semantic lowering
→ formal encoder assumptions
→ capability and numeric-compatibility routing
```

The schema does not contain solver expressions and the backend does not consume
the raw framework model. A retained concrete model is used separately by the
runtime observer for replay.

## Invariants

If schema construction succeeds:

1. the output name is non-empty;
2. the task and typed output kind agree;
3. feature names and semantic dtypes are normalized;
4. classification labels are unique JSON-compatible scalar values;
5. a binary decision policy has exactly two consistently oriented labels;
6. probability observability agrees with the recognized decision policy;
7. framework-specific metadata does not become generic semantic authority;
8. compatibility evidence remains explicit rather than inferred by a backend.

## Compatibility projections

`target`, `target_dtype`, and `target_source_dtype` remain read-only internal
projections of the typed output source of truth. They exist for migrated
internal callers and do not define a second model-output contract.

## Stability boundary

`ModelSchema`, its enum types, output variants, and registries live below
`toetra._*`. They are contributor interfaces inside the repository, not public
Python API. Normal callers should provide a supported model artifact to
`toetra.verify(...)`.

See the [ModelBridge overview](overview.md), the
[model-to-schema contract](../contracts/model-to-schema.md), and the
[public V1 profile](../public-v1-profile.md).
