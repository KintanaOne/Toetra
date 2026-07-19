# Changelog

All notable user-visible changes to FORML are recorded here.

The format follows Keep a Changelog principles. FORML uses semantic versioning
for its public Python API, report schemas, and documented V1 behavior.

## [1.0.0rc1] - 2026-07-19

### Added

- End-to-end `.forml` verification through the public `forml.verify` API.
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
