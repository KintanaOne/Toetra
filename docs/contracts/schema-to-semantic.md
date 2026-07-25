# Schema to Semantic Contract

> Status: Implemented for feature validation and P21.3 output observables; broader task contracts remain incremental  
> Scope: ModelSchema integration into semantic validation  
> Implementation: Schema-aware features and typed output observables are active  
> Audience: semantic maintainers, ModelBridge authors, compiler maintainers

## Purpose

The Schema to Semantic contract defines how ModelSchema participates in FORML semantic validation.

It answers the question:

```text
Do the DSL properties refer to things that exist in the model context?
```

This contract is required for true end-to-end FORML verification.

---

## Input

```text
SemanticValidatedAST candidate
+
ModelSchema
```

The semantic layer receives:

- FORML properties;
- resolved variables and attributes;
- model features;
- target information;
- task type;
- model metadata.

---

## Output

```text
SchemaAwareSemanticValidatedAST
```

This may still be represented as an enriched AST, but the semantic guarantees are stronger.

---

## Responsibilities

Schema-aware semantic validation should check:

| Concern | Example |
|---|---|
| Feature existence | `age` exists in `ModelSchema.features`. |
| Feature dtype | numeric comparisons only apply to numeric features. |
| Target compatibility | `target := label` matches schema target. |
| Task compatibility | `CLASSIFICATION` applies to classification model. |
| Property compatibility | property type is meaningful for model task. |
| Nullability constraints | nullable features may require special handling. |

---

## Why This Contract Exists

A property can be syntactically and semantically valid without being valid for a specific model.

Example:

```toetra
[BOUND]: check_at x => unknown_feature <= 10
```

The DSL binding may resolve `unknown_feature` to an entity, but the feature may not exist in the model schema.

This must be rejected before IR aggregation and backend lowering.

---

## Guarantees

If schema-aware validation succeeds:

- DSL feature references are known to the model schema;
- task-level predicates are compatible with the model task;
- target references are valid;
- feature dtypes are available to downstream type normalization;
- model constraints may be generated later from the same schema.

---

## Non-Goals

Schema-to-semantic validation must not:

- encode the model into a solver;
- produce CNF/DNF;
- aggregate full backend assertions;
- run the model;
- infer missing model schema silently.

---

## Failure Modes

This layer should reject:

- unknown feature references;
- incompatible dtype/operator combinations;
- target mismatch;
- property/problem mismatch with model task;
- missing required schema metadata;
- unsupported schema version.

---

## Miova Hooks

Miova may mutate ModelSchema or AST references by:

- renaming features;
- changing feature dtype;
- deleting target;
- changing task classification/regression;
- introducing unknown feature references;
- making nullable constraints inconsistent.

Expected outcome:

```text
Schema-inconsistent property → schema-to-semantic rejection
Schema-consistent property   → IR generation may continue
```

## Patch 21 Output-Observable Addendum

Schema-aware validation must apply the
[Model Output Observables Contract](model-output-observables.md):

- a scalar regression output may retain bare `target` syntax;
- a classification output requires an explicit `label` or
  `probability(label)` observable;
- labels are resolved by canonical value, not framework class index;
- observable availability and scalar type come from the typed output schema;
- unsupported observables and unknown labels fail at this boundary, before IR or
  backend routing.

The semantic layer validates public observables. It does not introduce logits,
decision functions, affine quantities, or backend symbols.
