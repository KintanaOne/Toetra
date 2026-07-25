# Toetra

Toetra is a Python framework and declarative language for specifying and verifying
behavioral properties of machine-learning models.

**Release status:** `1.0.0rc2` — V1 release candidate with regression and direct
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

## Regression property

```forml
model := "affine_score.joblib"
target := score

[BOUND]:
forall x0
with domain(x0.a: [0.0, 3.0])
=> target <= 7.0 using Z3
```

## Binary-classification property

```forml
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

```python
from toetra import verify

session = verify("policy.forml", model="model.joblib", dataset="reference.csv")
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

Text, HTML, Jupyter, records/DataFrame, and JSON schema v5 are supported.
Classification evidence is optional and additive.

## Documentation

- [Public V1 profile](docs/public-v1-profile.md)
- [1.0.0rc2 release notes](docs/releases/1.0.0rc2.md)
- [Getting started](docs/getting-started/overview.md)
- [Language reference](docs/language/overview.md)
- [Compatibility matrices](docs/generated/numeric-compatibility-matrices.md)
- [Architecture](docs/architecture/overview.md)
- [Public contract](docs/contracts/public-v1-contract.md)
- [Changelog](CHANGELOG.md)

## Release validation

```bash
make ci
make release-check
make review-bundle-check
```

These release gates are non-mutating.

## License

Toetra is licensed under the [Apache License 2.0](LICENSE).
