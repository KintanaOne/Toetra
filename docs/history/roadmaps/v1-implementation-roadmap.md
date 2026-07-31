# V1 foundations

> **Status:** Delivered before and through `1.0.0rc1`

The first V1 work established a complete verification system rather than a
collection of disconnected language or solver experiments.

## Language and compiler foundation

The Toetra Specification Language gained a layered compilation path from source
text to a concrete syntax tree, structural AST, semantic model, and two
intermediate representations. Explicit validation boundaries made syntax,
binding, typing, normalization, and executable support distinguishable.

Logical expressions were lowered through negation normal form and into the
backend-facing representation without making Z3 concepts part of the public
language.

## Model and verification foundation

`ModelSchema` became the boundary between trained model artifacts and formal
reasoning. The first public model bridge extracted a fitted single-output
sklearn `LinearRegression` into an auditable affine equation over transformed
numeric features.

Assertions, model constraints, point domains, and property requirements were
aggregated into a verification condition. The Z3 backend then supported proof,
counterexample, witness, no-witness, and unknown conclusions.

## Evidence and runtime foundation

The runtime added backend-neutral execution policy, numeric-compatibility
evidence, provenance, artifact fingerprints, and concrete replay against the
real estimator. Text, HTML, Jupyter, records/DataFrame, and JSON reporting were
designed as views of the same verification result.

## Release-candidate foundation

Reproducible wheel and source-distribution builds, clean-install checks,
end-to-end demonstrations, golden reports, and a reproducible review bundle
made the implemented route independently reviewable.

This sequence produced `1.0.0rc1` on 2026-07-19: the first public end-to-end
regression candidate. Its exact capability boundary is preserved in the
[release history](../../releases/1.0.0rc3.md) and current
[public V1 profile](../../public-v1-profile.md).
