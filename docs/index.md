# FORML

FORML is a declarative behavioral specification and verification framework for
machine-learning models.

The `1.0.0rc1` public profile provides an executable end-to-end route from a
`.forml` specification and a fitted scikit-learn `LinearRegression` model to Z3,
structured verification results, provenance, reports, and real-estimator replay.

## Start here

1. [Public V1 profile](public-v1-profile.md)
2. [Installation](getting-started/installation.md)
3. [First FORML property](getting-started/first-property.md)
4. [Language overview](language/overview.md)
5. [Generated compatibility matrices](generated/numeric-compatibility-matrices.md)

## V1 pipeline

```text
.forml specification + model/schema
→ parse and bind
→ semantic validation
→ IR1 and IR2
→ model assumptions
→ capability and numeric-compatibility routing
→ backend execution
→ result, provenance, report, and replay
```

## Built-in support

The V1 release candidate is intentionally narrow: finite transformed numeric
features, one sklearn `LinearRegression` output, affine encoding, homogeneous
`forall` or `exists` bindings, numeric domains and assertions, points/anchors,
and Z3.

The framework/model/backend interfaces remain generic. Vocabulary or extension
points for other systems are not implementation claims.

## Trust boundary

The built-in route reasons over the exact real-affine abstraction extracted from
the sklearn model. It is explicitly classified as `LOSSY` relative to concrete
floating-point execution. Every report states the semantic target and conclusion
scope instead of silently upgrading that result to a bit-exact guarantee.
