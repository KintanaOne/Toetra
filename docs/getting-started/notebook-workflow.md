# Notebook Model-Review Workflow

> Status: Implemented  
> Scope: Public `verify(...)` API, HTML reports and counterexample replay

## Purpose

A notebook user should not need to manipulate IR2, a backend router or Z3
objects. The supported workflow is:

```text
serialized model + reference dataset + .forml policy
→ verify(...)
→ VerificationSession
→ rich notebook report
→ optional counterexample replay
→ JSON / HTML artifacts
```

The executable example is:

```text
demo/notebooks/credit_risk_validation.ipynb
```

Run Jupyter from the repository root and open that file.

## Minimal notebook usage

```python
from dsl.runtime import verify

session = verify(
    "policy.forml",
    model="model.joblib",
    dataset="reference.csv",
)

session
```

Because `VerificationSession` implements `_repr_html_()`, Jupyter displays a
summary and one visual card per property. The same report data remains
available as ordinary Python objects:

```python
session.reports
session.results
session.exit_code
```

## Export artifacts

```python
session.write_json("artifacts/forml-report.json")
session.write_html("artifacts/forml-report.html")
```

The JSON contract is versioned and intended for CI or downstream automation.
The HTML document is self-contained, escaped and does not require JavaScript or
external stylesheets.

## Replaying a counterexample

The credit-risk notebook demonstrates the recommended validation step:

1. select the report whose status is `COUNTEREXAMPLE`;
2. convert exact solver rationals to numeric feature values;
3. reconstruct a pandas row in the model feature order;
4. call the original sklearn model;
5. compare its prediction with the model output encoded by FORML.

This checks that the formal counterexample is connected to the serialized model
that was actually reviewed.

## Current V1 boundary

The notebook operates on transformed numerical features and a supported affine
model. The current V1 does not encode preprocessing pipelines, symbolic
categories, nonlinear model families or nested/multiple quantifier semantics.
