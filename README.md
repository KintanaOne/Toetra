# FORML

**FORML** is a declarative, human-readable DSL for expressing **formal behavioral properties**
of machine learning models (robustness, fairness, stability, monotonicity, logic…).

It bridges the gap between **high-level requirements** and **formal verification tools**
such as **ERAN** or **Z3**.

---

## Why FORML?

Machine learning models are rarely tested beyond accuracy.

Yet, in practice, we often need answers to questions like:
- Is my model robust to noise or perturbations?
- Does it treat sensitive attributes fairly?
- Are its outputs bounded and logically consistent?

FORML allows these requirements to be expressed **explicitly**, **formally**, and **independently**
of the verification backend.

---

## Minimal Example

```forml
ROBUSTNESS:
at x0 in hyperball(L2, 0.01) := CLASSIFICATION.EQUAL()
```
The model must predict the same class for all small perturbations around x0.

## Executable end-to-end demo

The canonical demo trains and serializes a small affine scikit-learn model,
introspects it, compiles a FORML specification, injects typed domains and model
constraints into IR2, then executes the resulting tasks with Z3.

```bash
make demo-affine
```

Equivalent direct command:

```bash
python -m demo.affine_specification_constants_z3
```

The demo produces a proof, a counterexample and an existential witness without
leaving generated model or dataset files in the repository. See
[`demo/README.md`](demo/README.md) for details.

## Python verification API

A normal script can execute a policy without manipulating IR2, the backend
router or Z3 directly:

```python
from dsl.runtime import verify

session = verify(
    "policies/credit-risk.forml",
    model="models/credit-risk.joblib",
    dataset="data/reference.csv",
)

session.print()
session.write_json("artifacts/forml-report.json")
raise SystemExit(session.exit_code)
```

When `model` is omitted, the model declared in the FORML header is resolved
relative to the `.forml` file. See `demo/user_verify_script.py` for a complete
command-line example.

Run that script without preparing any files first:

```bash
make demo-user
```

Equivalent direct command:

```bash
python -m demo.user_verify_script --demo
```

For a real project, replace the paths in the Python example above with files
that exist in your repository.

## Jupyter and HTML reports

`VerificationSession` and `VerificationReport` expose a rich Jupyter
representation. Returning either object as the final cell expression displays
status cards, the normalized scope, the specification, counterexamples or
witnesses, and structured diagnostics:

```python
session = verify(
    "policy.forml",
    model="model.joblib",
    dataset="reference.csv",
)
session
```

A self-contained HTML artifact can be written without Jupyter:

```python
session.write_html("artifacts/forml-report.html")
```

See
[`demo/notebooks/credit_risk_validation.ipynb`](demo/notebooks/credit_risk_validation.ipynb)
for a complete model-review workflow, including replay of a formal
counterexample on the original sklearn model.

## Key Ideas

- FORML is declarative: you specify what must hold, not how to verify it

- Properties are backend-agnostic

- The language separates:
    - semantic intent (robustness, fairness, logic…)
    - scope (global, local, pairwise)
    - execution (ERAN, Z3, custom tools)

## Documentation

Full documentation is available in the docs/ directory:

- [scopes.md](docs/scope.md) — global, local and pairwise scopes

- [syntax.md — language syntax](docs/syntax.md)
  
- [semantic.md](docs/semantics.md)
  
- [properties.md](docs/properties.md) — semantic definition of property types

- backends.md — supported verification tools

## Project Status

FORML is an early-stage research and engineering project.
The core DSL, parser, and AST are functional.
Backend integrations are experimental and evolving.

## Contributing

- ✨ Contributions, suggestions, or improvements are welcome!
- Open issues to report bugs or suggest features
- Submit pull requests to improve the parser, DSL, or examples
- Star the repository if you find the idea promising

Let’s bring formal verification closer to real-world ML together 💡

# 🔐 License
Project licensed under MIT. See [LICENSE.md](LICENSE) for details.

# 👤 Author
Developed by KintanaOne
(Alias of a data scientist & formal methods enthusiast who believes that ML should be tested as rigorously as software.)