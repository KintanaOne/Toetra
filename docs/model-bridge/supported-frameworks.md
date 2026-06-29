# Supported Frameworks

> Status: partially implemented / evolving  
> Scope: ModelBridge framework support matrix  
> Priority: P1

## Purpose

This document tracks which machine learning frameworks are supported by ModelBridge and what level of support each framework has.

Framework support is not binary. A framework can be supported at several levels:

1. framework vocabulary;
2. detection;
3. loading;
4. introspection;
5. schema generation;
6. model constraint generation;
7. backend lowering;
8. end-to-end verification.

## Support Levels

| Level | Meaning |
|---|---|
| Vocabulary | Framework exists in FORML enum or documentation. |
| Loading | FORML can deserialize artifacts commonly used by the framework. |
| Detection | FORML can identify a loaded model object as belonging to the framework. |
| Introspection | FORML can extract metadata from the model object. |
| ModelSchema | FORML can produce a normalized schema. |
| Model constraints | FORML can derive model-side constraints. |
| Backend lowering | FORML can compile constraints into backend-specific query fragments. |
| End-to-end | FORML can run a property against that framework path. |

## Current Matrix

| Framework | Vocabulary | Loading | Detection | Introspection | ModelSchema | Model Constraints | Backend Lowering | End-to-End |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| scikit-learn | yes | partial | yes | yes | yes | planned | planned | planned |
| XGBoost | yes | partial | yes | yes | yes | planned | planned | planned |
| TensorFlow | yes | planned | planned | planned | planned | planned | planned | planned |
| PyTorch | yes | planned | planned | planned | planned | planned | planned | planned |
| ONNX | planned | planned | planned | planned | planned | planned | planned | planned |

## scikit-learn

### Current Support

scikit-learn currently has the most complete ModelBridge support.

Supported capabilities:

- detection through sklearn estimator base classes;
- feature detection through an external schema or dataset path;
- task detection for classifiers and regressors;
- schema generation;
- metadata extraction for common estimator attributes.

### Current Limitations

- feature detection may require a dataset path;
- feature bounds are not currently inferred;
- categorical domains are not explicitly represented;
- model behavior is not yet encoded as constraints;
- no backend-specific lowering is finalized.

## XGBoost

### Current Support

XGBoost support reuses sklearn-compatible introspection when available and enriches the schema metadata with XGBoost-specific fields.

Supported capabilities:

- detection through XGBoost model classes;
- reuse of sklearn-style feature and task introspection;
- framework override to `XGBOOST`;
- optional XGBoost metadata extraction.

### Current Limitations

- XGBoost objective metadata is extracted but not yet used for formal constraints;
- tree structure is not yet encoded;
- backend lowering is not finalized.

## TensorFlow

TensorFlow is part of the target framework vocabulary but is not yet implemented.

Planned work:

- loader support for SavedModel or Keras formats;
- detection of TensorFlow/Keras models;
- introspection of input signatures;
- schema generation;
- backend-aware model representation.

## PyTorch

PyTorch is part of the target framework vocabulary but is not yet implemented.

Planned work:

- loader support for `.pt` and `.pth` artifacts;
- detection of `torch.nn.Module`;
- introspection of input schema through user-provided schema or tracing;
- model constraint generation;
- backend-aware representation.

## ONNX

ONNX is not yet part of the current code path, but it is a natural future target because it can act as a framework-neutral model representation.

Potential role:

- bridge between training frameworks and verification backends;
- expose graph structure;
- simplify model lowering;
- support backend-agnostic analysis.

## Framework Support Criteria

A framework should not be declared end-to-end supported until all of the following are true:

1. model artifacts can be loaded or accepted;
2. framework detection is deterministic;
3. a normalized `ModelSchema` can be produced;
4. schema-aware semantic validation works;
5. model constraints can be generated;
6. backend lowering supports the model class;
7. golden samples exist;
8. Miova campaigns can challenge the path.

## Documentation Convention

Framework support pages should use the following status vocabulary:

| Status | Meaning |
|---|---|
| implemented | Code exists and is expected to work. |
| stabilizing | Code exists but contract is still being hardened. |
| partial | Some but not all expected capabilities exist. |
| planned | Architecturally required but not implemented. |
| research | Design direction is still exploratory. |

## Future Framework Pages

As support grows, each framework may get a dedicated page:

```text
model-bridge/frameworks/sklearn.md
model-bridge/frameworks/xgboost.md
model-bridge/frameworks/pytorch.md
model-bridge/frameworks/tensorflow.md
model-bridge/frameworks/onnx.md
```
