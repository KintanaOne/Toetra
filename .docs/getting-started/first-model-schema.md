# First Model Schema

> Status: Draft  
> Scope: ModelBridge onboarding  
> Implementation: Partially implemented

## Purpose

ModelBridge connects FORML specifications to real machine learning model artifacts.

Its first responsibility is to produce a normalized `ModelSchema`.

## ModelBridge pipeline

```text
model artifact
→ loader
→ loaded model
→ framework detection
→ introspector
→ ModelSchema
```

## What is a ModelSchema?

A `ModelSchema` is the normalized representation used by FORML to reason about a model.

It contains:

| Field | Purpose |
|---|---|
| `framework` | Detected ML framework |
| `model_type` | Concrete model class |
| `features` | Input feature schema |
| `target` | Target or output field |
| `task` | ML task type |
| `metadata` | Framework-specific metadata |

## Why does FORML need it?

The DSL can express properties such as:

```forml
age >= 18
score <= 0.9
CLASSIFICATION.EQUAL()
```

But FORML must know whether:

- `age` exists,
- `score` is a valid feature or output,
- the model is a classifier or regressor,
- the target is compatible with the declared property,
- the backend can encode the model.

ModelSchema is the bridge used to answer those questions.

## Current support

The current ModelBridge foundation supports:

- serialized model loading through dedicated loaders,
- framework detection,
- sklearn-style introspection,
- XGBoost introspection through sklearn-compatible behavior,
- normalized feature schema extraction,
- task detection for classifiers and regressors.

## V1 role

For the first V1, ModelSchema should support:

```text
semantic validation
+ model-aware feature checks
+ model constraint preparation
+ Z3 lowering support
```

## Example target flow

```text
model.joblib
+ dataset.csv
→ ModelBridge
→ ModelSchema
→ schema-aware semantic validation
→ model constraints
→ assertion aggregation
```

## Stabilization note

This document should be updated once the public ModelBridge API is finalized.
