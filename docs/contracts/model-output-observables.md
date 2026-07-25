# Model Output Observables Contract

> Status: Implemented — public in `1.0.0rc2`
> Normative ADR: [ADR-0023](../adr/ADR-0023-typed-model-outputs-and-observables.md)
> Scope: model schema, DSL output references, semantic typing, evaluation identity, IR1

## Purpose

This contract defines how Toetra represents a model output without assuming that
every output is one directly addressable numeric scalar.

It separates:

```text
output port
→ model evaluation at a point
→ public observable of that evaluation
→ optional internal model quantities
```

## Patch 21.4 implementation status

The schema portion of this contract is implemented through:

```text
ModelSchema.output_name
ModelSchema.output_schema
RegressionOutputSchema
ClassificationOutputSchema
UnknownOutputSchema
```

`ModelSchema.target`, `target_dtype`, and `target_source_dtype` are read-only
compatibility projections from that source of truth. Model evaluation identities
likewise use `output_name`, with a temporary `target_name` projection. P21.2 added
the declarative syntax and AST nodes. P21.3 binds those nodes to an output port and point, validates observable
availability and canonical labels, assigns scalar types, rejects ambiguous bare
classification targets, and interns one shared evaluation across observables.
P21.4 now preserves that result in IR1 through
`OutputObservableExpressionIR`, with one `ModelEvaluationIR` shared across label
and probability views. Model-family lowering and execution remain pending.

## Inputs and preconditions

A schema-aware compilation path receives:

- one selected model and its deterministic identity;
- one declared output port;
- a typed output schema;
- one or more semantically bound points;
- an output reference from the property assertion.

The current public V1 still has one selected output. This contract does not add
multi-output selection.

## Required output schema information

A typed output schema must provide enough information to answer:

1. What is the output port called?
2. What task kind does it represent?
3. Which public observables are available?
4. What is the scalar type of each observable?
5. For classification, which labels are legal and canonically ordered?
6. Which model semantic profile can interpret the observables?

The long-term source of truth must not be a loose combination of `task`,
`target_dtype`, and untyped metadata.

## Public observable vocabulary

| Observable kind | Type | Required source data | Target syntax |
|---|---|---|---|
| `REGRESSION_VALUE` | numeric scalar | scalar regression output schema | `target[x0]` |
| `PREDICTED_LABEL` | label scalar | classification label schema | `target[x0].label` |
| `CLASS_PROBABILITY` | numeric scalar | classification probability capability and resolved label | `target[x0].probability(label)` |

The label argument is a user-facing label value, never an internal class index.

## Evaluation identity invariant

One model evaluation is identified by:

```text
(model identity, point identity, output-port identity)
```

Observable kind and label argument are not part of evaluation identity.
Therefore these expressions reuse one evaluation:

```text
target[x0].label
target[x0].probability("approved")
target[x0].probability("rejected")
```

They remain distinct observable expressions.

## Binding and typing rules

### Scalar regression

A bare target reference is an implicit `REGRESSION_VALUE` observable when the
output schema exposes exactly one scalar regression value.

### Classification

A bare target reference is invalid because the intended observable is ambiguous.
The diagnostic must identify the legal explicit forms.

`target[x0].label` has the canonical label type declared by the output schema.

`target[x0].probability(label)` has numeric type and requires:

- one argument;
- a label compatible with the schema label type;
- a label present in the declared class set;
- a model semantic profile exposing class probabilities.

### Point selection

Explicit point indices follow ADR-0017. An omitted point is legal only when one
eligible default point exists.

## Information-preservation requirements

Every accepted output expression must preserve through IR1:

- output-port identity;
- point identity;
- observable kind;
- resolved label, when applicable;
- source location;
- source spelling or equivalent provenance needed for reporting;
- scalar type.

No downstream layer may reconstruct a label from a class index after the public
label identity has been discarded.

## Invalid combinations owned by the semantic boundary

The semantic layer must reject:

- a bare classification target;
- `.label` on a regression output;
- `.probability(...)` on a regression output;
- probability access when the model profile does not expose probabilities;
- an unknown label;
- an incompatible label type;
- arithmetic over a predicted label;
- ordering comparisons between labels unless a future contract defines them;
- any undeclared observable such as `.logit`, `.score`, or framework method name.

## Compatibility requirements

Existing scalar regression specifications retain their behavior.

Temporary Python aliases used during internal migration may exist, but serialized
schemas, provenance, and new code must move toward `output` terminology rather
than embedding a scalar-target assumption.

## Non-goals

- multiple output ports;
- top-k or ranking observables;
- confidence as a calibration guarantee;
- raw model method invocation from the DSL;
- public latent quantities;
- backend execution rules.

## Mutation and testing hooks

Required stable test groups are defined in the
[Binary Classification Test Matrix](../testing/binary-classification-test-matrix.md):

- `SCH-OUT-*` for output schemas;
- `PAR-OBS-*` and `AST-OBS-*` for syntax representation;
- `SEM-OBS-*` for binding and typing;
- `IR1-OBS-*` for evaluation and observable identity.
