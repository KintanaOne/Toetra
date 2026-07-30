# Toetra

Toetra is a declarative behavioral specification and formal-verification
framework for machine-learning models. It verifies properties over explicit
input domains and returns proof results, counterexamples or witnesses with
provenance and concrete model replay.

> **Current status:** `1.0.0rc3` is an evaluation release candidate, not the
> stable `1.0.0` release. It is currently installed from a source checkout or
> source archive and is not published on PyPI.

The candidate provides complete scikit-learn `LinearRegression` and direct
binary `LogisticRegression` routes to Z3. Its public Python API and executable
support profile are deliberately narrow and explicit.

## First use

From the repository root with Python 3.11 or 3.12:

```bash
python -m pip install .
python -m demo.quickstart.verify_model --demo
```

The self-contained demo should produce one `PROVED` result and one `WITNESS`.
Continue with:

1. [Installation and availability](getting-started/installation.md)
2. [First Toetra property](getting-started/first-property.md)
3. [Public V1 profile and limitations](public-v1-profile.md)
4. [Public Python API](api-reference/index.md)
5. [1.0.0rc3 release notes](releases/1.0.0rc3.md)
6. [Model output observables](language/model-output-observables.md)
7. [Compatibility matrices](generated/numeric-compatibility-matrices.md)

```text
.toetra + model/schema
→ parse and bind
→ semantic validation
→ IR1
→ model-semantic lowering
→ IR2 and model assumptions
→ compatibility routing
→ backend execution
→ report, provenance, and replay
```

The built-in routes reason over declared exact-real affine abstractions. Reports
preserve the trust boundary rather than claiming bit-exact framework execution.
