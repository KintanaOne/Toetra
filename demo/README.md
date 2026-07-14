# FORML demos

The `demo/` directory contains executable examples of the FORML compilation and
verification pipeline.

## Recommended demo — affine model end to end

Run:

```bash
python -m demo.affine_specification_constants_z3
```

This demo is self-contained. It:

1. creates a small dataset in a temporary directory;
2. trains a real scikit-learn `LinearRegression` model;
3. serializes the model with Joblib;
4. reconstructs a normalized `ModelSchema` through `ModelManager`;
5. compiles `demo/affine_specification_constants.forml`;
6. injects the affine model equation and the typed DSL domains into IR2;
7. routes each task to Z3 according to backend capabilities;
8. invokes the public `forml.verify(...)` API;
9. builds backend-neutral `VerificationReport` objects;
10. renders a proof, a counterexample and an existential witness through the
    shared FORML reporting layer;
11. deletes the generated model and dataset automatically.

The trained model is:

```text
score = 2 * a + 1
```

The FORML source uses global specification constants and a typed input domain:

```forml
minimum_a := 0.0
maximum_a := 3.0
maximum_score := 7.0
witness_score := 5.0
```

It executes three properties:

| Property | Expected result | Explanation |
|---|---|---|
| `target <= maximum_score` | `PROVED` | On `a ∈ [0, 3]`, the maximum score is 7. |
| `target < maximum_score` | `COUNTEREXAMPLE` | `a = 3` produces `score = 7`. |
| `target == witness_score` under `exists` | `WITNESS` | `a = 2` produces `score = 5`. |

The complete runtime path is:

```text
.forml source
→ parser and AST builder
→ semantic binding and scalar typing
→ symmetric scalar IR1
→ NNF normalization
→ DSL domain assumptions
→ affine model assumption
→ IR2 requirements
→ backend capability routing
→ recursive affine Z3 translation
→ backend-neutral VerificationResult
→ user-facing VerificationReport
→ shared text renderer
```

No binary model or generated CSV is committed to the repository.

## Public Python API

The demo returns a `VerificationSession`, the same object used by application
code:

```python
from demo.affine_specification_constants_z3 import run_demo

_schema, session = run_demo()
session.print()
session.write_json("forml-verification-report.json")
```

A standalone command-line-style example is available in
`demo/user_verify_script.py`.

Run it immediately without creating a model, dataset or policy file:

```bash
make demo-user
```

Equivalent direct command:

```bash
python -m demo.user_verify_script --demo \
    --json-output artifacts/forml-report.json
```

The self-contained mode trains a temporary affine model and executes
`demo/user_verify_policy.forml`. The generated model and dataset are deleted
automatically.

For an existing project, provide real paths from your repository:

```bash
python -m demo.user_verify_script path/to/policy.forml \
    --model path/to/model.joblib \
    --dataset path/to/reference.csv \
    --json-output artifacts/forml-report.json
```

When `--model` is omitted, the model reference from the FORML header is resolved
relative to the specification file. Missing paths are reported as concise CLI
errors rather than Python tracebacks. The process exits with the session's
CI-friendly status code.

The generated file uses the versioned
`forml.verification-report-collection` schema. Exact Z3 rationals are retained
as numerator/denominator pairs instead of being rounded.

## Credit-risk notebook

The repository also contains a notebook-oriented model-review example:

```text
demo/notebooks/credit_risk_validation.ipynb
```

It trains a small affine credit-risk score from transformed numerical features,
loads a packaged example policy, displays the session through its native Jupyter
HTML representation, selects `session.first_counterexample`, replays it with
`finding.replay()`, and exports JSON and standalone HTML with
`session.write_artifacts(...)`. No solver-value conversion or feature-name
parsing is written by the notebook user.

Open the notebook from the repository root or directly from `demo/notebooks/`.
Its first code cell locates the source checkout before importing the public
`forml` package. This bootstrap is specific to the repository demo; installed
users can begin directly with `from forml import verify`. The notebook is
self-contained and creates model/data artifacts in a temporary directory.
Preprocessing remains explicitly outside the current V1 contract.

## Earlier incremental demos

These scripts document earlier milestones and remain useful for focused
inspection:

```bash
python -m demo.end_to_end_z3
python -m demo.affine_model_assumption_z3
python -m demo.model_encoder_linear_z3
python -m demo.linear_bound_with_domain_z3
```

The recommended demo above is the canonical example for the current numerical
and affine V1 profile.

## Requirements

Install the project dependencies before running the demos:

```bash
pip install -e .
```

The main demo requires scikit-learn, pandas, Joblib and `z3-solver`, which are
already declared by the project.
