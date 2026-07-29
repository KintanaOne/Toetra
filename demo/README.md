# Toetra demos

The `demo/` directory contains executable examples grouped by audience and
verification profile:

```text
demo/
├── quickstart/      # public verify(...) workflow for application code
├── regression/      # public LinearRegression examples and notebook
├── classification/  # public binary-classification examples and Cleveland workspace
└── internals/       # compiler, IR2 and backend-oriented engineering examples
```

## Quickstart — verify an existing model

Run the self-contained command-line example:

```bash
make demo-quickstart
```

Equivalent direct command:

```bash
python -m demo.quickstart.verify_model --demo \
    --json-output artifacts/toetra-report.json
```

The demo trains a temporary affine model and executes an embedded copy of
`demo/quickstart/verification_policy.toetra`. Generated model and dataset files
are deleted automatically.

The Python file is intentionally standalone. After Toetra is installed, it can
be copied to any directory and run without the repository or the adjacent
policy file:

```bash
cp demo/quickstart/verify_model.py /tmp/toetra-quickstart.py
cd /tmp
python toetra-quickstart.py --demo
```

Its imports are limited to the public `toetra` facade and declared runtime
dependencies. The clean-wheel release probe executes this copied-file scenario.

For an existing project, provide paths from your repository:

```bash
python -m demo.quickstart.verify_model path/to/policy.toetra \
    --model path/to/model.joblib \
    --dataset path/to/reference.csv \
    --json-output artifacts/toetra-report.json
```

When `--model` is omitted, the model reference from the Toetra header is resolved
relative to the specification file. Missing paths are reported as concise CLI
errors rather than Python tracebacks. The process exits with the session's
CI-friendly status code.

The generated JSON uses the versioned `toetra.verification-report-collection`
schema. Exact backend rationals are retained as numerator/denominator pairs
instead of being rounded.

## Regression — affine model end to end

Run:

```bash
make demo-regression
```

Equivalent direct command:

```bash
python -m demo.regression.affine_regression
```

This self-contained example:

1. creates a small dataset in a temporary directory;
2. trains a real scikit-learn `LinearRegression` model;
3. serializes the model with Joblib;
4. reconstructs a normalized `ModelSchema` through `ModelManager`;
5. compiles `demo/regression/affine_regression_policy.toetra`;
6. injects the affine model equation and typed DSL domains into IR2;
7. routes each task according to backend capabilities;
8. invokes the public `toetra.verify(...)` API;
9. builds backend-neutral `VerificationReport` objects;
10. renders a proof, a counterexample and an existential witness;
11. deletes the generated model and dataset automatically.

The trained equation is:

```text
score = 2 * a + 1
```

The Toetra source uses global specification constants and a typed input domain.
It executes three properties:

| Property | Expected result | Explanation |
|---|---|---|
| `target <= maximum_score` | `PROVED` | On `a ∈ [0, 3]`, the maximum score is 7. |
| `target < maximum_score` | `COUNTEREXAMPLE` | `a = 3` produces `score = 7`. |
| `target == witness_score` under `exists` | `WITNESS` | `a = 2` produces `score = 5`. |

The complete runtime path is:

```text
.toetra source
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

The Python demo can also be reused directly:

```python
from demo.regression.affine_regression import run_demo

_schema, session = run_demo()
session.print()
session.write_json("toetra-verification-report.json")
```

### Credit-risk notebook

The notebook-oriented model-review workflow is:

```text
demo/regression/credit_risk_validation.ipynb
```

It trains a small affine credit-risk score from transformed numerical features,
loads the packaged public policy, displays the native Jupyter report, selects
and replays a counterexample, and exports JSON and standalone HTML artifacts.
No solver-value conversion or feature-name parsing is written by the notebook
user. Preprocessing remains explicitly outside the current V1 contract.

## Classification — binary policy

Run:

```bash
make demo-classification
```

Equivalent direct command:

```bash
python -m demo.classification.binary_classification_policy
```

The demo trains a direct binary scikit-learn `LogisticRegression`, verifies a
label proof, a replayable counterexample, a probability witness and pairwise
label equality, then checks concrete replay through the public API.

The matching notebook is:

```text
demo/classification/binary_classification_policy.ipynb
```

Both public notebooks are tested when launched from their own directory and
from the repository root. Their source-checkout bootstrap does not depend on
the shell's original import path.

### Cleveland heart-disease workspace

A realistic data-preparation and training workspace is available at:

```text
demo/classification/cleveland/
```

It keeps its immutable source dataset under `data/` and writes generated local
artifacts under an ignored `artifacts/` directory. See the scenario README for
its current V1 boundary.

## Internal engineering examples

These examples expose compiler, IR2, model-encoding and Z3 details. They are
useful to contributors, but they are not examples of the stable public API:

```bash
python -m demo.internals.compiler_pipeline_z3
python -m demo.internals.affine_model_assumption_z3
python -m demo.internals.linear_regression_encoder_z3
python -m demo.internals.linear_bound_with_domain_z3
```

## Requirements

Install the project dependencies before running the demos:

```bash
pip install -e .
```

The public demos require scikit-learn, pandas, Joblib and `z3-solver`, which are
already declared by the project.
