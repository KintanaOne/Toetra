# Model Constraints

> Status: implemented for affine regression and the P21.6 binary logistic latent quantity  
> Scope: ModelBridge to logical verification pipeline  
> Priority: P0

## Purpose

Model constraints are the logical or semantic constraints derived from `ModelSchema` and model metadata.

They are not the same as user DSL assertions.

The DSL expresses verification intent. Model constraints describe the model-side facts and restrictions that must be considered when building a verification problem.

## Why Model Constraints Exist

A backend query cannot be built from DSL assertions alone.

The final verification problem needs to combine:

- user-defined assertions;
- semantic constraints from scopes and bindings;
- domain constraints;
- neighborhood constraints;
- model input constraints;
- model task constraints;
- backend capability constraints.

Model constraints provide the model-side portion of that problem.

## Position in the Pipeline

```text
ModelSchema
    ↓
Model Constraint Generation
    ↓
ModelConstraintIR
    ↓
Assertion Aggregation
    ↓
Lowering / Minimization
    ↓
BackendQuery
```

## Relationship with Assertion Aggregation

Assertion aggregation should combine several sources of constraints:

```text
UserAssertionIR
+ SemanticConstraintIR
+ ScopeConstraintIR
+ ModelConstraintIR
+ BackendCapabilityConstraintIR
= AggregatedAssertionSet
```

Model constraints therefore join the logical pipeline before lowering and backend-specific encoding.

## Constraint Categories

### Feature Existence Constraints

Ensure that DSL-referenced features exist in the model schema.

Example:

```text
feature(age) exists
```

### Feature Type Constraints

Ensure that operations are compatible with feature types.

Example:

```text
age.dtype ∈ {INT, FLOAT}
age <= 30 is valid
```

### Nullability Constraints

Represent whether missing values are possible or allowed.

Example:

```text
nullable(age) = false
```

### Input Dimensionality Constraints

Ensure that backend encodings preserve the expected input dimension.

Example:

```text
len(input_vector) = n_features_in
```

### Task Compatibility Constraints

Ensure that the declared FORML problem is compatible with the model task.

Example:

```text
CLASSIFICATION.EQUAL requires task = classification
REGRESSION.BETWEEN requires task = regression
```

### Target Constraints

Ensure that the target referenced by FORML is coherent with the schema.

Example:

```text
target = "label"
```

### Framework Metadata Constraints

Optional constraints derived from framework-specific metadata.

Examples:

```text
classes = [0, 1]
objective = "binary:logistic"
```

### Symbolic Model Encoding Constraints

Backend-independent constraints describing the model behavior itself.

Examples:

```text
target[x] = w · x + b
internal_oriented_decision[x] = w · x + b
```

P21.6 introduces `AffineModelQuantityConstraintIR2` for the second form. The
quantity is internal and remains distinct from public output observables.

These constraints are critical for robustness and pairwise properties.

## Planned Intermediate Representation

A future representation may introduce:

```text
ModelConstraintIR
├── FeatureConstraintIR
├── TypeConstraintIR
├── DomainConstraintIR
├── TaskConstraintIR
├── TargetConstraintIR
├── InputShapeConstraintIR
└── ModelBehaviorConstraintIR
```

This representation should remain backend-independent until lowering.

## Semantic Preservation

Model constraint generation must preserve the meaning of the model schema.

It must not invent unsupported facts.

For example:

- if feature bounds are unknown, FORML should not silently assume them;
- if task type is unknown, task compatibility should fail or remain unresolved;
- if feature names are unavailable, the system should require an external schema or produce diagnostics.

## Invariants

1. Model constraints must be derived from explicit schema or metadata.
2. Unknown model facts must remain unknown, not guessed.
3. Constraint generation must be deterministic for the same schema.
4. Model constraints must remain backend-independent before lowering.
5. Framework-specific metadata must be normalized or isolated.
6. Model behavior constraints must be traceable to the model artifact and framework.
7. Generated constraints must be distinguishable from user-authored assertions.

## Diagnostics

Model constraint generation should produce precise diagnostics when:

- a referenced feature does not exist;
- a feature type is incompatible with an operation;
- the model task is incompatible with a property;
- feature metadata is missing;
- target metadata is ambiguous;
- backend lowering requires information not present in the schema.

## Example

Given the DSL expression:

```toetra
[ROBUSTNESS]: forall baseline, candidate => CLASSIFICATION.EQUAL()
```

And a model schema:

```text
task = classification
features = {age, income, score}
target = label
```

The future model constraint layer may contribute:

```text
model_task = classification
model_input_features = {age, income, score}
output_semantics = class_label
x and x' share the same model input schema
y = model(x)
y' = model(x')
```

These constraints then join the DSL assertion during aggregation.

## Open Questions

- Should model constraints be generated before or after IR2 normal forms?
- Should model behavior constraints live in IR2 or a dedicated ModelIR?
- Should symbolic model encoding be backend-independent or backend-specific?
- How should unsupported models expose partial schemas?
- How much model metadata is required for the first Z3 backend?
