# ADR-0023 — Represent Model Outputs as Typed Ports and Declarative Observables

> Status: Accepted — public in `1.0.0rc2`
> Date: 2026-07-20
> Scope: DSL output references, AST, semantic typing, IR1 evaluation identity, ModelSchema, reporting

## Implementation note

Patch 21 implements this ADR across schema, AST, semantic binding, IR1,
reporting, and replay. `output_name` and `output_schema` are the normalized source
of truth. Legacy `target`, `target_dtype`, `target_source_dtype`, and `target_name`
accessors remain read-only compatibility projections for the Toetra 1.x line;
new code uses output-oriented names. Their removal requires a later major version.

## Context

The public V1 profile currently supports one numeric regression output. Across the
compiler, the word `target` therefore often denotes all of the following at once:

1. the output port declared by the specification header;
2. the evaluation of the model at a point;
3. the scalar value produced by that evaluation;
4. the symbol connected to the backend equation.

That equivalence stops being valid for classification. One model evaluation may
expose several user-relevant values without becoming several evaluations:

- a predicted label;
- a probability estimate for each label;
- internal quantities used to implement the model decision.

Treating every one of those values as a separate `target` would duplicate model
evaluations, leak framework vocabulary into the language, and make future model
families define incompatible meanings for the same syntax.

## Decision

Toetra will distinguish an **output port**, a **model evaluation**, a **public
output observable**, and an **internal model quantity**.

### Output port

The header declaration identifies a model output port:

```text
target := decision
```

The keyword `target` remains the user-facing reference to that declared port. It
does not imply that the port is directly a numeric scalar.

### Model evaluation

A model evaluation identifies one invocation of one model output at one point:

```text
(model identity, point identity, output-port identity)
```

Repeated references to different observables of the same output at the same point
must reuse the same evaluation identity.

### Public output observable

A public output observable is a typed, declarative view of an evaluation. The
initial vocabulary is:

| Task | Public observable | Target syntax |
|---|---|---|
| Scalar regression | regression value | `target[x0]` |
| Classification | predicted label | `target[x0].label` |
| Classification | class probability estimate | `target[x0].probability(label)` |

A class probability estimate is the probability-like value exposed by the model
for a named label. The term does not imply that the estimator is statistically
calibrated.

### Internal model quantity

A bridge may introduce mathematical quantities required to implement or verify an
observable. Such quantities are not automatically part of the DSL. Examples
include a decision value, a log-odds value, a tree path indicator, or an ensemble
vote count.

Internal quantities may appear in lowering evidence, backend artifacts, replay
diagnostics, and technical reports. They must not be confused with the observable
requested by the user.

### Compatibility behavior for bare `target`

The existing short form remains valid when the output schema provides one
unambiguous scalar regression value:

```text
target[x0] <= 0.20
```

For classification, a bare `target[x0]` is ambiguous and must be rejected with a
diagnostic directing the user to an explicit observable:

```text
target[x0].label
target[x0].probability("approved")
```

The existing default-point rules remain unchanged: an omitted point is accepted
only when exactly one eligible point exists.

### Schema direction

`ModelSchema` will evolve toward a typed output schema. Compatibility projections
such as `target`, `target_dtype`, or `target_name` may remain temporarily while
callers migrate, but they are not the long-term source of truth.

Conceptually:

```text
ModelOutputSchema
├── output_name
├── task_kind
└── observable_schema
```

The exact Python class hierarchy remains an implementation decision of Patch 21.1,
provided it preserves the contracts in this ADR.

## Rationale

This design keeps the language centered on user intent while allowing the bridge
to expose different model-family semantics. It also prevents evaluation identity
from being multiplied by presentation choices.

The distinction is reusable beyond logistic classification:

- a classifier without probabilities may expose `label` but not `probability`;
- a calibrated wrapper may expose a different probability contract;
- a ranking model may later expose rank or ordering observables;
- a structured-output model may expose task-specific observable projections.

## Consequences

- `TargetRefNode` can no longer be assumed to be a scalar expression in all cases.
- Internal names that encode a scalar-target assumption must be reviewed and
  migrated incrementally.
- Semantic typing becomes schema-dependent for output observables.
- IR1 must preserve evaluation identity separately from observable identity.
- Reporting must identify the requested observable separately from any internal
  quantity used by the backend.
- Existing scalar regression syntax remains compatible.

## Non-goals

This ADR does not:

- add classification syntax to the parser;
- define logistic lowering;
- expose a generic `score` observable;
- expose logits, decision functions, framework methods, or backend symbols;
- add multi-output models;
- change the `1.0.0rc1` public support profile.

## Alternatives considered

### Make `target` mean the predicted label for classifiers

Rejected because the same token would mean a numeric value for regression and a
label for classification, while leaving no principled place for probability
properties.

### Expose framework methods directly

Forms such as `predict_proba`, `decision_function`, or `classes_[1]` were rejected
because they make the DSL framework-centric and couple specifications to model
implementation details.

### Expose a generic `score`

Rejected because `score` may mean a decision value, business score, probability,
margin, ranking score, or estimator evaluation metric. The term is too ambiguous
to freeze as a public observable.

## Impact on Toetra

This ADR amends the scalar-output assumptions described by ADR-0008, ADR-0014,
and ADR-0017 for the Patch 21 target architecture. It does not retroactively
change the executable `1.0.0rc1` contract frozen by ADR-0022.

## P21.9 reporting implementation amendment

The typed-output distinction is now reflected in reporting. Classification
labels and probabilities are grouped under a per-evaluation structure, while
latent model quantities remain technical auxiliary evidence. The historical
scalar `assignments.outputs` field is not reinterpreted. Concrete replay obtains
public and internal views through a framework-neutral model-observer protocol.
