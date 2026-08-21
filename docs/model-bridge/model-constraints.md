# Model equations and schema constraints

> **Status:** Implemented for the public affine routes
>
> **Scope:** schema-time validation and formal model assumptions

The implementation has no general `ModelConstraintIR` hierarchy. Model-derived
knowledge enters the pipeline at two explicit boundaries.

## Schema-time constraints

Semantic validation uses `ModelSchema` to check:

- target name and output port;
- feature existence and normalized dtype;
- regression versus classification task compatibility;
- class labels and observable type;
- point inputs against the ordered feature contract.

These checks fail before IR2. They are not solver assertions.

## Formal model equations

The selected builder first constructs immutable Model IR. Compiler lowering
then receives:

- normalized `ModelSchema`;
- normalized Model IR;
- exact requested `ModelEvaluationIR` identities;
- optional `ModelEncodingContext`.

It returns model-tagged `AssumptionIR2` values.

### Linear regression

For each requested point:

```text
target[point] = intercept + Σ coefficientᵢ × point.featureᵢ
```

### Direct binary logistic regression

For each requested point:

```text
oriented_decision_value[point]
    = oriented_intercept + Σ oriented_coefficientᵢ × point.featureᵢ
```

Orientation aligns the equation with the declared positive class. Public label
and probability observables are lowered separately by the model semantic
profile.

## Evaluation identity

Compiler lowering does not infer a point from a scope. It receives exact
structured identities and must produce:

- exactly one equation for every requested evaluation;
- no equation for an unrequested evaluation;
- no duplicate or disconnected output identity.

IR2 guardrails validate these invariants.

## Assumption ownership

Model equations remain distinguishable from domain and anchor assumptions:

```text
AssumptionSource.MODEL
```

They are collected into `VerificationTaskIR2.assumptions` and contribute to the
executable verification condition and capability requirements.

## Soundness

Model IR construction derives coefficients and intercepts from fitted model
state. Lowering combines that computation with explicit schema orientation,
dtype, output identity, and requested evaluations. Missing or unsupported state
is rejected at the owning boundary.

The numeric compatibility layer records that the formal affine equation uses an
exact-real abstraction of serialized framework floating-point parameters. Model
equations alone do not claim bit-exact equivalence to every concrete framework
execution.

## Extension rule

Adding a schema or introspector is insufficient. A new public model route also
requires semantic meaning, Model IR construction, compiler lowering, backend
capability, numeric policy, reporting, replay, and end-to-end/release tests.

See the [model constraints contract](../contracts/model-constraints.md),
[model-semantic lowering contract](../contracts/model-semantic-lowering.md), and
[public extension rule](../public-v1-profile.md#extension-rule).
