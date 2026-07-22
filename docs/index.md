# FORML

FORML is a declarative behavioral specification and verification framework for
machine-learning models.

The `1.0.0rc2` profile provides complete sklearn `LinearRegression` and direct
binary `LogisticRegression` routes to Z3, structured reports, provenance, and
concrete replay.

## Start here

1. [Public V1 profile](public-v1-profile.md)
2. [1.0.0rc2 release notes](releases/1.0.0rc2.md)
3. [Installation](getting-started/installation.md)
4. [First FORML property](getting-started/first-property.md)
5. [Model output observables](language/model-output-observables.md)
6. [Compatibility matrices](generated/numeric-compatibility-matrices.md)

```text
.forml + model/schema
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
