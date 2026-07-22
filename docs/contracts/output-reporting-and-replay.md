# Model Output Reporting and Replay Contract

> Status: Implemented by P21.9 for scalar regression and the initial binary-classification profile  
> Scope: IR2 traceability, backend assignments, reports, JSON, text/HTML/Jupyter renderers, concrete replay  
> Public release status: additive JSON v5 evidence public in `1.0.0rc2`

## Purpose

A verification result must preserve the distinction between:

1. the output observable requested by the user;
2. the internal model quantity used by the proof;
3. the value reconstructed from the formal backend assignment; and
4. the value observed by executing the concrete model.

No renderer or replay path may collapse these four roles into one generic
"model output" value.

## Per-evaluation identity

Reporting groups evidence by the existing model-evaluation identity:

```text
(model identity, point identity, output port)
```

Observable selection is not part of that identity. A label property and two
probability properties at the same point therefore share one report evaluation
and one concrete model invocation.

Each classification evaluation may contain:

- the predicted label reconstructed from the formal decision quantity;
- reconstructed probabilities for every declared class;
- internal quantities marked as technical evidence;
- the native decision policy;
- one or more lowering traces retaining the source intent.

## Source intent preservation

IR2 retains the original pre-lowering IR1 specification separately from the
canonical lowered formula. User-facing `specification` fields and concrete
property replay use this original formula.

For example, the report must state:

```forml
target[applicant].probability("approved") >= 0.80
```

and may then explain the internal lowering. It must not replace the public
specification with an expression over `oriented_decision_value`.

## Formal reconstruction

When a backend returns an assignment for the internal oriented decision value
`z`, FORML may derive report views for the initial binary-logistic profile:

```text
predicted label:
    positive label when z > native decision threshold
    negative label otherwise

positive-class probability:
    sigmoid(z)

negative-class probability:
    1 - sigmoid(z)
```

The label follows the exact native boundary policy. Reconstructed probabilities
are presentation evidence, not exact-real proof atoms: they are evaluated with
50 significant decimal digits and identified as
`reconstructed_from_oriented_decision_value`.

The proof continues to rely on the canonical constraint and the certified
threshold interval from `LoweringEvidence`, not on the displayed sigmoid value.

## Lowering trace

Every rendered lowering trace includes, when available:

- public observable, label and operator;
- property threshold and concrete/formal property value;
- property satisfaction and margin;
- semantic profile and transformation versions;
- internal quantity and canonical constraint;
- canonical margin;
- exact threshold expression;
- certified lower and upper threshold bounds;
- selected bound, published precision, working precision and guard digits;
- numeric compatibility classification and permitted conclusions.

The native model threshold and the property threshold are separate fields.

## Assignment roles

Internal model quantities remain `auxiliary` assignments. They must never be
moved into the historical `assignments.outputs` collection or exposed as the
value of the public output port.

For classification, the public label and probabilities live under
`model_evaluations`, not under the legacy scalar-output assignment list.

## JSON v5 additive evolution

P21.9 keeps the frozen report envelope:

```text
forml.verification-report / schema_version 5
```

It adds the optional top-level `model_evaluations` field. Existing v5 fields are
not reinterpreted, and reports without classification evidence remain byte-for-
structure compatible with the existing v5 golden contract.

Historical v1-v5 fixtures remain in the repository. A future breaking change to
an existing field would require a new schema version; this additive field does
not.

## Runtime observer protocol

Concrete replay obtains model values through a framework-neutral
`ModelRuntimeObserver` protocol:

```text
supports(schema, model) -> bool
observe(schema, model, inputs) -> ModelObservation
```

The generic replay layer must not inspect a concrete estimator class. The first
registered implementation is the sklearn observer, which normalizes:

- `predict` into a regression value or predicted label;
- `predict_proba` into label-keyed class probabilities;
- `decision_function` into the internal oriented decision value for the initial
  binary-logistic profile.

Other frameworks can register observers without modifying replay logic.

## Concrete replay comparison

Replay compares each view independently:

| View | Comparison |
|---|---|
| predicted label | exact equality |
| class probability | absolute error under replay tolerance |
| internal decision quantity | absolute error under replay tolerance |
| scalar regression output | historical absolute-error comparison |
| original property | concrete reevaluation of the preserved source IR1 formula |
| scope restriction | concrete reevaluation when present and supported |

A replay is consistent only when every available formal/concrete comparison is
within tolerance and the original property agrees with the expected status:

- `COUNTEREXAMPLE` expects the concrete property to be false;
- `WITNESS` expects the concrete property to be true.

Missing required features, observables or model quantities cause an explicit
`ReplayUnavailableError`; replay is never silently partial.

## Soundness boundary

Concrete replay validates one concrete witness or counterexample. It does not
upgrade an approximate universal proof into a concrete-source proof and does not
replace numeric compatibility policy.

Reconstructed probabilities in a report describe the formal assigned quantity.
Concrete probabilities in replay come from the runtime observer. The difference
between them is reported explicitly.

## Non-goals

P21.9 does not:

- expose logit or decision-function syntax in the DSL;
- add calibrated or custom-threshold wrappers;
- add probability equality or arithmetic;
- make internal quantities public outputs;
- amend the `1.0.0rc1` executable support profile;
- replace P21.8.1 interval evidence with displayed reconstructed probabilities.
