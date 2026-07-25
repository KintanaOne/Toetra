# Changelog

## [Unreleased]

### Changed

- Renamed the canonical specification extension from `.forml` to `.toetra`.
- Renamed grammar artifacts and parser entry points to the Toetra Specification
  Language identity.
- Removed runtime acceptance of the legacy `.forml` extension.

## [Unreleased]

### Changed

- Renamed the Python distribution and sole public import namespace to `toetra`.
- Moved packaged examples to `toetra.examples`; no `forml` import alias is retained.
## [1.0.0rc2] - 2026-07-22

### Added

- Public direct binary sklearn `LogisticRegression` verification route.
- Declarative label/probability observables, pairwise relations, reporting,
  replay, and clean-install classification smoke tests.

### Fixed

- Stable Decimal provenance canonicalization and certified logistic-threshold
  interval materialization.
- Tolerance-aware three-valued replay at numeric ordering boundaries, avoiding
  false exact-real/IEEE-754 witness mismatches.

### Compatibility

- JSON report schema v5 remains additive and the `LinearRegression` route is
  unchanged.

All notable user-visible changes to Toetra are recorded here.

The format follows Keep a Changelog principles. Toetra uses semantic versioning
for its public Python API, report schemas, and documented V1 behavior.

## [1.0.0rc1] - 2026-07-19

### Added

- End-to-end `.toetra` verification through the public `toetra.verify` API.
- First-class points, anchors, homogeneous quantifiers, indexed model evaluations,
  numeric domains, specification constants, and scalar arithmetic.
- Single-output scikit-learn `LinearRegression` ModelBridge encoding.
- Z3 execution with proof, counterexample, witness, no-witness, and unknown results.
- Real-estimator replay for counterexamples and witnesses.
- Backend-neutral numeric compatibility registry and generated matrices.
- Backend-neutral execution policy with timeout, resource, cancellation, status,
  duration, and diagnostic evidence.
- Verification provenance and content fingerprints.
- Text, HTML, Jupyter, records/DataFrame, and JSON v5 reporting.
- Reproducible wheel, sdist, clean-install, and review-bundle checks.

### Changed

- The public V1 guarantee is explicitly scoped to the extracted real-affine model.
- CI is non-mutating and validates Python 3.11 and 3.12.
- Documentation and package metadata now describe the executable V1 profile.

### Known limitations

- Only the built-in sklearn `LinearRegression` → affine encoder → Z3 route is
  end-to-end supported.
- The built-in numeric route is not a bit-exact floating-point proof.
- Preprocessing, categorical reasoning, alternating quantifier execution,
  nonlinear models, and additional built-in backends are deferred.
