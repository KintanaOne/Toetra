# Toetra

Toetra is a Python framework and declarative language for specifying and
formally verifying behavioral properties of machine-learning models. It turns a
property and an explicit input domain into a proof result, counterexample, or
witness, with provenance and concrete model replay.

> **Project status — `1.0.0rc3`:** this is an evaluation release candidate, not
> the stable `1.0.0` release. It is not currently published on PyPI. Install it
> from a source checkout or source archive while the candidate is exercised in
> real use.

## What Toetra verifies

The built-in V1 routes answer questions such as:

- is an affine regression output always below a declared bound?
- does increasing one input preserve an expected monotonic relation?
- does a direct binary logistic model keep a label or probability property over
  an input domain?
- if a property is false or satisfiable, which concrete input demonstrates it?

Toetra verifies the declared property against an explicit exact-real affine
abstraction extracted from the supported model. It does not claim correctness
of the training data, preprocessing, deployment system, or arbitrary
floating-point execution.

| Route | Supported candidate profile |
|---|---|
| Regression | fitted single-output scikit-learn `LinearRegression` |
| Classification | direct fitted binary scikit-learn `LogisticRegression` |
| Inputs | finite transformed numeric features |
| Logic | homogeneous `forall` or `exists`, points, anchors, domains, affine arithmetic, Boolean properties |
| Backend | Z3 |
| Evidence | reports, provenance, counterexamples or witnesses, concrete replay |

The [Public V1 profile](docs/public-v1-profile.md) is the authoritative support
contract.

## Try the release candidate

From the repository root with Python 3.11 or 3.12:

```bash
python -m pip install .
python -m demo.quickstart.verify_model --demo
```

The self-contained quickstart trains a temporary scikit-learn
`LinearRegression` model and checks two regression properties through the
public API. It should finish with one `PROVED` result and one `WITNESS`, then
remove its temporary model and dataset.

See [Installation](docs/getting-started/installation.md) for environment and
development setup, or [Getting started](docs/getting-started/overview.md) for
the complete first-use path.

## Regression property

<!-- toetra-doc-snippet: regression-bound -->
```toetra
model := "affine_score.joblib"
target := score

maximum_score := 7.0

[BOUND]:
forall x0
with domain(x0.a: [0.0, 3.0])
=> target[x0] <= maximum_score using Z3
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

Users express labels and probabilities. Logits, framework methods, class
indices, latent quantities, and backend symbols remain internal.

## Python API

<!-- toetra-doc-snippet: verify-session -->
```python
from toetra import verify

session = verify("policy.toetra", model="model.joblib", dataset="reference.csv")
session.print()
session.write_artifacts("artifacts", formats={"json", "html"})
raise SystemExit(session.exit_code)
```

`toetra.verify(...)` remains the public Python execution entry point for
embedded use. The installed `toetra` and `python -m toetra` process interfaces
now provide solver-free `validate` and `inspect` commands, executable
verification, and delayed replay of archived evidence:

```bash
toetra verify policy.toetra \
  --model model.joblib \
  --dataset reference.csv \
  --format json \
  --artifacts-dir artifacts/toetra
```

The command returns `0` for positive conclusions, `1` for a formal failure, and
`2` for an inconclusive result. Archived counterexamples and witnesses can then
be checked against the exact supplied artifacts without rerunning the solver:

```bash
toetra replay artifacts/toetra/toetra-verification-report.json \
  --specification policy.toetra \
  --model model.joblib \
  --dataset reference.csv \
  --format json
```

Only `init` remains scheduled for the final P28 increment.

## Reading a result

| Status | Meaning |
|---|---|
| `PROVED` | the universal property holds in the declared formal scope |
| `COUNTEREXAMPLE` | a violating assignment was found |
| `WITNESS` | a satisfying assignment was found for an existential property |
| `NO_WITNESS` | no satisfying assignment exists in the declared formal scope |
| `UNKNOWN` | Toetra cannot make a sound positive or negative conclusion |

Text, HTML, Jupyter, records/DataFrame, and JSON schema v6 reports are supported.
Classification evidence is optional and additive.

## Numeric guarantee

The built-in encoders construct exact-real affine abstractions from framework
floating-point state. Reports identify numeric compatibility, semantic target,
lowering evidence, provenance, and concrete replay. Toetra does not silently
claim bit-exact IEEE-754 equivalence.

Non-exact probability thresholds use certified directed `logit(p)` intervals
and restricted conclusion policies.

## Explicit limitations

Multiclass models, nonlinear encoders, symbolic preprocessing, threshold or
calibration wrappers, custom decision thresholds, probability
equality/edge-thresholds/arithmetic, alternating quantifiers, and built-in
non-Z3 backends are outside the V1 profile.

In particular, pass already transformed numeric features. Toetra `1.0.0rc3`
does not reconstruct or verify a scikit-learn `Pipeline`.

## Demos and documentation

```bash
make demo-quickstart
make demo-regression
make demo-classification
```

The classification demo covers label proof, a replayable counterexample, a
probability witness, and pairwise label equality.

- [1.0.0rc3 release notes](docs/releases/1.0.0rc3.md)
- [Getting started](docs/getting-started/overview.md)
- [Public Python API](docs/api-reference/index.md)
- [Language reference](docs/language/overview.md)
- [Compatibility matrices](docs/generated/numeric-compatibility-matrices.md)
- [Architecture](docs/architecture/overview.md)
- [Public contract](docs/contracts/public-v1-contract.md)
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)

## Development and validation

```bash
python -m pip install -e ".[dev,docs]"
make ci
```

On Windows hosts where Smart App Control blocks Ruff's unsigned native binary,
run the complete non-Ruff local gate and keep hosted CI authoritative for lint:

```bash
make ci-local
```

Release evidence is split into explicit gates:

```bash
make ci
make demo-check
make release-check
make review-bundle-check
```

After committing a clean candidate, reproduce that entire journey from a fresh
clone:

```bash
make outside-in-check
```

The frozen repository structure is documented in the
[repository contract](docs/contracts/repository-contract.md).

## License

Copyright © 2025–2026 Tina RANDRIANARIJAONA-DUBIN. See the
[copyright and ownership notice](COPYRIGHT.md) for the scope of this claim and
the separate treatment of third-party material.

Toetra is source-available for noncommercial use under the
[PolyForm Noncommercial License 1.0.0](LICENSE). Use outside the purposes
permitted by that license requires a separate written agreement; see
[Commercial licensing](COMMERCIAL_LICENSE.md).

This is not an open-source license under the Open Source Definition. The public
license does not grant the right to use Toetra for a commercial hosted service,
managed service, or SaaS offering. Redistributed third-party material keeps its
own license and attribution; see [Third-party material](THIRD_PARTY.md).
