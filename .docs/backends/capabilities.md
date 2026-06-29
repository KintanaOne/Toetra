# Backend Capabilities

> Status: Planned / critical for backend orchestration  
> Scope: Backend metadata, compatibility checking, strategy selection  
> Priority: P1

## Purpose

A backend capability describes what a verification backend can support.

FORML should not assume that every backend can handle every property, model type, logical form, or constraint. Capability declarations make backend selection explicit, explainable, and testable.

This document answers:

```text
How does FORML know whether a backend can verify a given property?
```

## Why capabilities matter

Without explicit capabilities, backend selection becomes fragile and implicit.

For example:

- an SMT solver may support symbolic linear constraints but not arbitrary neural network verification;
- an abstract interpretation backend may support robustness but not fairness;
- a backend may require CNF-like clauses;
- a backend may accept only specific model families;
- a backend may produce approximate results instead of exact proof/counterexample results.

Capabilities prevent invalid backend calls and enable meaningful diagnostics.

## Capability dimensions

A backend capability should describe several independent dimensions.

| Dimension | Examples | Purpose |
|---|---|---|
| Property support | `ROBUSTNESS`, `BOUND`, `MONOTONICITY`, `FAIRNESS` | Which FORML properties can be handled. |
| Problem support | `CLASSIFICATION`, `REGRESSION`, `CLUSTERING` | Which ML task families are supported. |
| Model support | sklearn, XGBoost, neural networks, linear models | Which model representations can be encoded. |
| Logical form support | NNF, CNF, DNF, arbitrary boolean tree | Which IR2/lowered forms can be consumed. |
| Constraint support | linear, nonlinear, categorical, neighborhood, domain | Which constraint categories are valid. |
| Result support | proof, counterexample, unknown, diagnostics | What the backend can report. |
| Execution support | local, external process, API, library call | How the backend is executed. |

## Suggested capability model

A future backend capability object may follow this structure:

```python
@dataclass(frozen=True)
class BackendCapability:
    name: str
    supported_properties: set[EnumProperty]
    supported_problems: set[EnumProblem]
    supported_frameworks: set[EnumModelFramework]
    supported_model_types: set[str]
    supported_logical_forms: set[str]
    supported_constraint_kinds: set[str]
    result_modes: set[str]
    exact: bool
    supports_counterexamples: bool
    supports_timeout: bool
```

This is not a required implementation yet. It is a design target for backend orchestration.

## Compatibility checking

Before executing a backend, FORML should check:

```text
BackendCapability
+ Property type
+ Problem type
+ ModelSchema
+ AggregatedAssertionSet
+ LoweredQuery
→ compatible / incompatible / partially compatible
```

Possible outcomes:

| Outcome | Meaning |
|---|---|
| Compatible | Backend can execute the query. |
| Incompatible | Backend cannot support the request. |
| Partially compatible | Backend can support part of the query but not all constraints. |
| Requires lowering | Backend needs a specific logical form or simplified query. |
| Requires model encoding | Backend needs a symbolic model representation first. |

## Early failure principle

Backend incompatibility should fail before execution.

FORML should prefer:

```text
clear diagnostic before backend execution
```

over:

```text
late backend crash or unclear solver error
```

## Example diagnostics

A capability checker should be able to produce diagnostics such as:

```text
Backend 'z3' cannot encode model type 'RandomForestClassifier' without a model encoder.
```

```text
Backend 'eran' supports robustness properties but not pairwise fairness properties.
```

```text
Backend 'box' supports approximate bounds but cannot produce exact counterexamples.
```

## Relationship with backend orchestration

Backend orchestration depends on capabilities.

```text
LoweredQuery
+ ModelConstraints
+ BackendCapabilities
→ Backend selection
```

If the user explicitly requests a backend, capabilities validate that choice.

If the user does not request a backend, capabilities allow FORML to select one automatically in the future.

## Relationship with contracts

Backend capabilities should be covered by contracts:

| Contract | Responsibility |
|---|---|
| `ir-to-backend.md` | Defines accepted input to backend compilation. |
| `type-normalization.md` | Ensures capability checks use normalized enums/types. |
| `errors.md` | Defines backend incompatibility diagnostics. |
| `mutation-boundaries.md` | Defines how Miova can mutate backend configs and capabilities. |

## Miova testing strategy

Miova can test backend capabilities by mutating:

- supported property sets;
- backend names;
- logical form requirements;
- model framework metadata;
- execution options;
- timeout settings;
- capability declarations.

Expected outcomes:

| Mutation | Expected result |
|---|---|
| Unsupported property added to query | Backend incompatibility diagnostic. |
| Unknown backend name | Backend selection failure. |
| Unsupported model framework | Capability rejection. |
| Missing required logical form | Lowering requirement diagnostic. |

## Design invariant

A backend must never be selected only because its name appears in the DSL.

Backend selection must be validated against capabilities.

