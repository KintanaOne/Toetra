# ERAN Backend

> Status: Planned / research-oriented backend candidate  
> Scope: Neural network robustness verification and abstract interpretation  
> Priority: P1 / research direction depending on model support

## Purpose

The ERAN backend represents the class of neural-network-specific verification backends.

Unlike a general SMT solver, ERAN-like systems are designed to reason about neural network robustness through abstract domains and specialized verification algorithms.

This document defines how Toetra should treat ERAN as a future backend candidate.

## Role in Toetra

The ERAN backend should be considered when Toetra needs to verify properties such as:

- local robustness;
- stability under perturbations;
- bounds over neural network outputs;
- abstract-domain-based guarantees.

The intended flow is:

```text
.toetra property
→ semantically validated AST state
→ IR1 / NNF
→ VerificationTaskIR2 + assumptions
→ capability and numeric route qualification
→ ERAN-private translation artifact
→ ERAN execution
→ VerificationResult
```

## Backend fit

ERAN-like backends are typically relevant when:

| Condition | Relevance |
|---|---|
| Model is neural-network-like | High |
| Property is robustness-related | High |
| Perturbation neighborhood is explicit | High |
| Backend supports the model format | Required |
| Exact logical counterexample is needed | Depends on backend |

## Model requirements

An ERAN backend will likely require model-specific formats or conversions.

Possible requirements:

- ONNX representation;
- TensorFlow or PyTorch model export;
- supported activation functions;
- bounded input domains;
- explicit perturbation metric;
- normalized feature ranges.

This means ModelBridge alone is not enough. A future model export or model encoder layer may be required.

## Relationship with ModelBridge

ModelBridge provides normalized metadata:

```text
Model artifact
→ ModelSchema
```

For ERAN, an additional layer may be needed:

```text
ModelSchema
+ loaded model
→ ERAN-compatible model representation
```

This should remain separate from semantic validation.

## Candidate property support

| Toetra property | Candidate support |
|---|---|
| ROBUSTNESS | Strong candidate |
| STABILITY | Possible |
| BOUND | Possible for output bounds |
| MONOTONICITY | Backend-dependent |
| FAIRNESS | Not primary target |
| LOGIC | Only if reducible to supported constraints |

## IR requirements

ERAN may not require CNF/DNF in the same way as an SMT backend.

However, IR2 is still useful for:

- extracting robustness conditions;
- separating cases;
- normalizing property structure;
- detecting unsupported logical patterns;
- preparing backend-specific query generation.

## Capability declaration

ERAN capability metadata should include:

- supported model formats;
- supported layers/operations;
- supported perturbation metrics;
- supported abstract domains;
- supported property types;
- exactness or approximation mode;
- counterexample support;
- timeout behavior.

## Diagnostics

ERAN diagnostics should explain unsupported conditions clearly.

Examples:

```text
ERAN backend requires a neural network model representation, but ModelSchema describes sklearn.RandomForestClassifier.
```

```text
ERAN backend does not support the requested perturbation metric 'L1'.
```

```text
ERAN backend cannot encode the current logical assertion because it contains unsupported disjunctions.
```

## Result normalization

ERAN-native results should be normalized into Toetra results.

Possible Toetra result statuses:

| Status | Meaning |
|---|---|
| verified | Property holds under backend assumptions. |
| violated | Counterexample or adversarial point found. |
| inconclusive | Backend could not prove or refute. |
| unsupported | Query/model/property not supported. |
| failed | Backend execution failure. |

## Miova testing opportunities

Miova can challenge ERAN integration by mutating:

- perturbation metrics;
- epsilon values;
- model framework metadata;
- property types;
- logical assertions;
- backend options;
- expected abstract domains.

This is especially useful because neural verification backends often have strict input and model constraints.

## Non-goals

Initial ERAN documentation should not imply ERAN support is implemented.

This backend should remain clearly marked as planned or research-oriented until Toetra has:

- a supported neural model format;
- model export or encoding;
- backend query generation;
- execution integration;
- result normalization.

