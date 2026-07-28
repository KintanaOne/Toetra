# Toetra

Toetra is a Python framework and declarative language for specifying and verifying
behavioral properties of machine-learning models.

**Release status:** `1.0.0rc3` — V1 release candidate with regression and direct
binary-classification routes.

## V1 scope

```text
finite transformed numeric features
+ sklearn LinearRegression or direct binary LogisticRegression
+ scalar, label, probability, and pairwise-label properties
+ affine model encoding and explicit semantic lowering
+ homogeneous forall/exists bindings, points, anchors, numeric domains
+ Z3
→ PROVED / COUNTEREXAMPLE / WITNESS / NO_WITNESS / UNKNOWN
```

Toetra remains framework-neutral and backend-neutral at its architectural
boundaries. Scikit-learn and Z3 are the first complete built-in routes.

## Installation

```bash
python -m pip install .
```

For development:

```bash
python -m pip install -r requirements-dev.txt
make ci
```

On Windows hosts where Smart App Control blocks Ruff's unsigned native binary,
run the complete non-Ruff local gate and keep hosted CI authoritative for lint:

```bash
make ci-local
```

## Regression property

<!-- toetra-doc-snippet: regression-bound -->
```toetra
model := "affine_score.joblib"
target := score

maximum_score := 7.0

[BOUND]:
forall x0
with domain(x0.a: [0.0, 3.0])
=> target <= maximum_score using Z3
```

## Binary-classification property

<!-- toetra-doc-snippet: binary-probability -->
```toetra
model := "binary_decision.joblib"
target := decision

[LOGIC]:
forall applicant
with domain(applicant.income: [3.0, 6.0])
=> target[applicant].probability("yes") >= 0.80 using Z3
```

Users express labels and probabilities. Logits, framework methods, class indices,
latent quantities, and backend symbols remain internal.

## Demos

```bash
make demo-quickstart
make demo-classification
```

The classification demo covers label proof, a replayable counterexample, a
probability witness, and pairwise label equality.

## Python API

<!-- toetra-doc-snippet: verify-session -->
```python
from toetra import verify

session = verify("policy.toetra", model="model.joblib", dataset="reference.csv")
session.print()
session.write_artifacts("artifacts", formats={"json", "html"})
raise SystemExit(session.exit_code)
```

## Numeric guarantee

The built-in encoders construct exact-real affine abstractions from framework
floating-point state. Reports identify numeric compatibility, semantic target,
lowering evidence, provenance, and concrete replay. Toetra does not silently
claim bit-exact IEEE-754 equivalence.

Non-exact probability thresholds use certified directed `logit(p)` intervals and
restricted conclusion policies.

## Explicit limitations

Multiclass models, nonlinear encoders, symbolic preprocessing, threshold or
calibration wrappers, custom decision thresholds, probability equality/edge
thresholds/arithmetic, alternating quantifiers, and built-in non-Z3 backends are
outside the V1 profile.

## Reports

Text, HTML, Jupyter, records/DataFrame, and JSON schema v6 are supported.
Classification evidence is optional and additive.

## Documentation

- [Public V1 profile](docs/public-v1-profile.md)
- [1.0.0rc3 release notes](docs/releases/1.0.0rc3.md)
- [Getting started](docs/getting-started/overview.md)
- [Public Python API](docs/api-reference/index.md)
- [Language reference](docs/language/overview.md)
- [Compatibility matrices](docs/generated/numeric-compatibility-matrices.md)
- [Architecture](docs/architecture/overview.md)
- [Public contract](docs/contracts/public-v1-contract.md)
- [Changelog](CHANGELOG.md)

## Release validation

```bash
make ci
make demo-check
make release-check
make review-bundle-check
```

Run the four gates explicitly from a clean checkout. They are the durable
quality, demonstration, distribution, and review-bundle boundaries. The frozen
repository structure is documented in the
[repository contract](docs/contracts/repository-contract.md).

## License

Toetra is licensed under the [Apache License 2.0](LICENSE).
