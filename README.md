# FORML

FORML is a Python framework and declarative language for specifying and verifying
behavioral properties of machine-learning models.

**Release status:** `1.0.0rc1` — public V1 contract frozen for validation.

FORML answers questions such as:

- Does a model output remain within a declared bound?
- Does a universal property hold over a numeric domain?
- Can FORML find a witness satisfying an existential property?
- Can a counterexample be replayed on the original estimator?

## V1 scope

The V1 release candidate deliberately supports a narrow, auditable path:

```text
numeric transformed features
+ single-output scikit-learn LinearRegression
+ affine model encoding
+ homogeneous forall or exists bindings
+ numeric intervals and finite sets
+ scalar arithmetic and Boolean assertions
+ inline or referenced points/anchors
+ Z3 backend
→ PROVED / COUNTEREXAMPLE / WITNESS / NO_WITNESS / UNKNOWN
```

FORML is backend-neutral at its architectural boundaries. Z3 is the only built-in
V1 execution backend, and scikit-learn `LinearRegression` is the only built-in
end-to-end model family.

## Installation from source

FORML requires Python 3.11 or 3.12.

```bash
python -m pip install .
```

For development:

```bash
python -m pip install -r requirements-dev.txt
make ci
```

## Minimal FORML specification

```forml
model := "affine_score.joblib"
target := score

maximum_score := 7.0

[BOUND]:
forall x0
    with domain(x0.a: [0.0, 3.0])
    => target <= maximum_score
    using Z3
```

## Run the self-contained demo

The canonical demo trains a temporary affine model, verifies universal and
existential properties, and prints structured results:

```bash
make demo-user
```

It does not leave generated model or dataset files in the repository.

## Python API

```python
from forml import verify

session = verify(
    "policy.forml",
    model="model.joblib",
    dataset="reference.csv",
)

session.print()
session.write_artifacts("artifacts", formats={"json", "html"})
raise SystemExit(session.exit_code)
```

The public application API is exposed from `forml`. Modules under `dsl`, `model`,
IR layers, and backend adapters are internal extension surfaces rather than the
normal user entry point.

## Numeric guarantee

The built-in V1 route encodes a floating-point sklearn affine model as an exact
real-valued affine abstraction for Z3. The route is therefore classified as
`LOSSY` with conclusions restricted to the declared semantic target:

```text
forml.real_affine_extracted_model
```

FORML does not silently claim bit-exact IEEE-754 equivalence. Reports include the
numeric compatibility rule, semantic target, execution policy, provenance, and
fingerprints needed to interpret the conclusion honestly.

## Explicit V1 limitations

The following remain outside the built-in V1 profile:

- trees, ensembles, neural networks, and nonlinear model encoders;
- classifiers and multi-output models;
- reconstruction or symbolic encoding of preprocessing pipelines;
- categorical or string reasoning in the backend;
- executable alternating quantifiers;
- built-in backends other than Z3;
- bit-exact floating-point proofs;
- distributed execution, dashboards, registries, and organizational governance.

Custom registries and adapters can extend several boundaries, but an extension is
not considered supported until it declares capabilities, numeric compatibility,
execution behavior, and tests.

## Reports and reproducibility

FORML produces text, HTML, Jupyter, records/DataFrame, and JSON reports. JSON
schema version **5** is frozen for the FORML 1.x public contract. Incompatible
changes require a new schema version.

Each verification report identifies its specification, model, dataset or schema,
route, execution policy, software environment, and compiler configuration through
structured provenance and content fingerprints.

## Documentation

- [Public V1 profile](docs/public-v1-profile.md)
- [Getting started](docs/getting-started/overview.md)
- [Language reference](docs/language/overview.md)
- [Generated compatibility matrices](docs/generated/numeric-compatibility-matrices.md)
- [Architecture](docs/architecture/overview.md)
- [Public V1 contract](docs/contracts/public-v1-contract.md)
- [Changelog](CHANGELOG.md)

## Release validation

```bash
make ci
make release-check
make review-bundle-check
```

The release checks build reproducible wheel and source distributions, install the
wheel in a clean environment outside the checkout, and verify the review bundle.

## License

FORML is licensed under the [Apache License 2.0](LICENSE).
