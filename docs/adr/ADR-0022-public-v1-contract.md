# ADR-0022 — Freeze the public V1 contract

> **Amended by ADR-0026:** `1.0.0rc2` adds the direct binary `LogisticRegression` route while preserving this ADR as the historical `rc1` freeze.


- **Status:** Accepted
- **Date:** 2026-07-19

## Context

Toetra's compiler and runtime reached an executable numeric-affine path, while
older public documentation still mixed implemented behavior, target architecture,
and research directions. A V1 cannot be trustworthy if users cannot distinguish
built-in support from extension vocabulary.

## Decision

Toetra `1.0.0rc1` freezes a deliberately narrow public profile:

- Python 3.11–3.12;
- single-output scikit-learn `LinearRegression` over transformed numeric inputs;
- affine ModelBridge encoding;
- homogeneous universal or existential bindings, points/anchors, numeric domains,
  scalar assertions, and implemented numeric-affine restrictions;
- Z3 execution;
- public `toetra.verify` API;
- JSON report schema v5.

The built-in numeric route remains explicitly `LOSSY` and scoped to
`toetra.real_affine_extracted_model`. Broader framework and backend vocabulary is
an extension architecture, not a V1 support claim.

The repository license is Apache-2.0. README, package metadata, documentation,
and release artifacts must agree.

## Consequences

- Public onboarding can be executable and precise.
- New model families and backends can be added without redefining the V1 route.
- Incompatible JSON changes require a new schema version.
- Internal modules remain evolvable; the `toetra` facade is the normal user API.
- The release candidate must pass non-mutating CI, reproducible distribution,
  clean-install, and review-bundle gates.
