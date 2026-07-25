# Notebook Model-Review Workflow

> Status: Implemented  
> Scope: Public `toetra.verify(...)` API, rich reports and automatic replay

## Purpose

A notebook user should not manipulate IR2, backend routers, Z3 objects or solver
number representations. The supported workflow is:

```text
serialized model + reference dataset + Toetra policy
→ verify(...)
→ VerificationSession
→ rich notebook report
→ optional replay
→ JSON / HTML artifacts
```

The executable example is:

```text
demo/regression/credit_risk_validation.ipynb
```

## Minimal notebook usage

```python
from toetra import verify

session = verify(
    "policy.toetra",
    model="model.joblib",
    dataset="reference.csv",
)

session
```

Because `VerificationSession` implements `_repr_html_()`, Jupyter displays a
summary and one card per property. Common inspection helpers are direct:

```python
session.to_dataframe()
session.proved
session.counterexamples
session.witnesses
session.exit_code
```

## Replaying a counterexample

Artifact-based sessions retain the loaded estimator. Replaying a formal
counterexample therefore requires no solver parsing or feature-name surgery:

```python
counterexample = session.first_counterexample
assert counterexample is not None

replay = counterexample.replay()
replay.to_dataframe()
```

The replay:

1. converts exact backend values to standard Python values;
2. reconstructs the model input in schema feature order;
3. calls the original estimator's `predict(...)`;
4. compares the model output with the FORML backend output;
5. reports the absolute error and consistency result.

When `verify(...)` is called with a `ModelSchema` only, no estimator is attached.
An estimator can then be supplied explicitly with `finding.replay(model)`.

## Export artifacts

```python
paths = session.write_artifacts(
    "artifacts/",
    formats={"json", "html"},
)
```

The JSON contract is versioned for CI and automation. The HTML document is
self-contained and does not require JavaScript or external stylesheets.

## Current V1 boundary

Replay operates on transformed numerical features and estimators exposing a
`predict(...)` method. Preprocessing pipelines, symbolic categories, nonlinear
model families and nested/multiple quantifier semantics remain outside the
current executable profile.
