# Model constraints contract

> **Status:** Implemented for the public affine model routes
>
> **Scope:** `ModelSchema` validation and model `AssumptionIR2` generation

Model-derived knowledge enters Toetra through two boundaries.

## Schema-semantic boundary

`ModelSchema` is used to validate:

- ordered feature existence and dtype;
- target/output identity;
- task and output-observable compatibility;
- class labels and model family;
- point inputs required by the property.

These are semantic checks. They do not become solver formulas.

## Model-encoding boundary

The model encoder receives:

```text
ModelSchema
+ requested ModelEvaluationIR identities
+ optional ModelEncodingContext
```

and returns model-tagged `AssumptionIR2` values.

Implemented equations are:

- scalar affine output for fitted single-output sklearn `LinearRegression`;
- affine oriented decision quantity for direct fitted binary sklearn
  `LogisticRegression`.

## Required guarantees

1. Every coefficient, intercept, label orientation, feature order, dtype, and
   output identity comes from explicit schema or fitted model state.
2. Exactly one equation is emitted for each requested evaluation.
3. No unrequested, duplicate, or disconnected equation is emitted.
4. Model assumptions remain backend-neutral.
5. Internal model quantities remain distinct from public output observables.
6. Unsupported model families or incomplete metadata fail explicitly.
7. Numeric compatibility evidence describes the abstraction used by the
   equation.

## Composition

Model assumptions join domain and anchor assumptions inside
`VerificationTaskIR2`. The implementation has no `ModelConstraintSet`,
`ModelConstraintIR`, or `AggregatedAssertionSet` runtime class.

Backend capabilities are not model assumptions; they are checked later by the
router.

## Patch 21 Model Quantities and Observable Lowering

Patch 21 established a boundary that remains part of the public classification
contract:

- model encoders materialize internal model quantities from the fitted model;
- framework-neutral semantic profiles lower public label and probability
  observables to constraints over those quantities.

An encoder must not erase the public observable or define DSL vocabulary. After
lowering, a backend receives canonical constraints, while reporting and
provenance retain both the source intent and the generated model quantities.

See the [binary classification profile](binary-classification-profile.md).

## Failure ownership

| Failure | Owner |
|---|---|
| invalid/missing schema metadata | ModelBridge or semantic validation |
| no semantic profile for a public observable | model-semantic lowerer |
| no encoder for the model family | encoder factory |
| malformed evaluation equation | encoder/IR2 guardrail |
| structurally valid equation unsupported by a backend | router |

## Extension

A new model encoder is not public support by itself. The
[public extension rule](../public-v1-profile.md#extension-rule) also requires
semantics, capabilities, numeric policy, execution, reporting, replay, tests,
documentation, and release validation.
