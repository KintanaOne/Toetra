# Changelog

## [Unreleased]

### Added

- Added the P28.4 `replay` workflow for archived JSON v6 witness and
  counterexample evidence, with strict provenance and property-fingerprint
  matching, repeated property selection, text/JSON/HTML output, logical replay
  statuses `0`/`1`/`2`, atomic output, and an installed-wheel replay probe.
- Added the P28.3 `verify` workflow with text, exact JSON v6, and HTML
  primary output, logical process statuses `0`/`1`/`2`, individually atomic
  JSON/HTML artifacts, a manifest-last `toetra.run-manifest` completion marker,
  output-collision protection, and installed-wheel verification probes.
- Added the P28.2 `validate` and `inspect` workflows with syntax, semantic,
  and executable dry-run boundaries, stable JSON schemas, atomic primary output,
  backend translation without solving, SIGTERM status handling, and
  installed-wheel CLI probes.
- Added the P28.1 CLI foundation with equivalent installed `toetra` and
  `python -m toetra` entry points, metadata-backed `--version`, the accepted
  command index, reserved process status `3`, and text/JSON stderr diagnostics.
- Accepted the P28 CLI and automation contract for `validate`, `inspect`,
  `verify`, `replay`, and `init`, including process statuses, stream ownership,
  machine-readable diagnostics, artifact manifests, cancellation, and MLOps
  integration boundaries; only the `init` handler remains pending after P28.4.
- Added a public-snapshot audit gate, a full-history audit command, and explicit
  CC BY 4.0 provenance for the redistributed UCI processed Cleveland dataset.
- Added an outside-in gate that clones the exact clean candidate, follows the
  public README journey in a new Python environment, runs all durable release
  gates, and rejects checkout drift.
- Added the controlled-exposure runbook and an unauthenticated public-surface
  probe that binds the exposed commit to the review-bundle digest.

### Changed

- Published `toetra replay` as a solver-free reconstruction workflow over the
  existing concrete replay engine, without widening the nine-symbol public
  Python facade or introducing a serialized private IR contract.
- Published `toetra verify` as the process adapter over the existing shared
  verification session without changing the Python API or JSON v6 report
  contract, while invalidating stale completion manifests before artifact
  replacement and deferring Z3 imports until an executable backend is needed.
- Reused one private routed pre-execution plan across `validate`, `inspect`, and
  `verify`, while keeping backend solver execution exclusive to verification.
- Made the nine-symbol public Python facade lazy so CLI help and version queries
  do not import compiler, model, backend, or solver implementations.
- Replaced Apache-2.0 with PolyForm Noncommercial 1.0.0 for Toetra-originated
  code and documentation, documented the separate commercial-licensing route,
  and protected that route from ungoverned outside contributions.
- Reworked the public README and onboarding path around an explicit
  source-installed `1.0.0rc3` evaluation status, a literal self-contained first
  run, expected conclusions, supported routes, and visible limitations without
  claiming PyPI, CLI, or stable-release availability.
- Separated public repository exposure, the CLI automation surface, and stable
  release hardening into independent milestones, and accepted a dedicated
  public repository readiness contract without changing `1.0.0rc3`.
- Made the public quickstart independently copyable outside the repository,
  added clean-wheel execution of that copied script, and verified both public
  notebooks from the repository root and their own directories.
- Aligned terminal text, HTML/Jupyter, records/DataFrame, and JSON v6 reporting
  around the same logical conclusion, backend-execution context, numeric trust
  boundary, evidence, provenance, and diagnostics without changing the JSON
  schema.
- Normalized backend-runner, translation, execution-policy, and technical
  execution failures at `verify(...)`, while preserving timeout, resource,
  cancellation, and solver-unknown outcomes as reportable `UNKNOWN` results.
- Normalized model-encoder, model-semantic, numeric-compatibility, and backend-
  routing failures at `verify(...)`, distinguishing invalid integration inputs,
  unsupported routes, and technical routing failures with stable diagnostics.
- Normalized specification, model, and reference-dataset artifact failures at
  `verify(...)`, distinguishing invalid inputs from loaded but unsupported
  model integrations while preserving stable diagnostics and private causes.
- Normalized syntax, CST-to-AST construction, and semantic validation failures
  at `verify(...)` while preserving their distinct owning stages, source
  locations, stable codes, remediation hints, and chained private causes.
- Stopped relabeling semantic validation failures as parser errors and stopped
  exposing Lark `UnexpectedInput` subclasses from the parser entry point.
- Accepted the public failure boundary: the three existing error families now
  expose stable diagnostic codes, owning stages, optional remediation and source
  context, while private causes remain available through exception chaining.
- Froze the `1.0.0rc3` documentation around the nine-symbol public API,
  as-built compiler/runtime pipeline, explicit language support levels, and
  separate model-family, framework-adapter, and backend extension paths.
- Added canonical CI-checked public snippets, consolidated delivered work into a
  chronological project history, and replaced stale active planning with the
  remaining evaluation, release, and post-V1 questions.
- Froze the repository contract, added exact source-to-distribution
  package inventory checks, and introduced durable repository and demo
  validation gates.
- Split binary-classification semantic lowering into a stable profile facade
  plus focused logical, label, probability, pairwise, and shared support
  modules without changing canonical IR or evidence.
- Split counterexample replay into stable public data models, orchestration,
  three-valued evaluation, and rendering modules without changing replay outputs.
- Consolidated the Cleveland classification workspace under `demo/`, grouped
  repository scripts by responsibility, and separated project history from
  active planning.
- Migrated all installable code to the canonical `src/toetra/` layout.
- Consolidated the former top-level `dsl` and `model` implementation packages
  into private responsibility-based `toetra._*` namespaces.
- Restricted wheel package discovery to the single `toetra` top-level package
  and strengthened clean-install checks against obsolete namespaces.
- Switched grammar loading to packaged resources so parsing works from wheels,
  source distributions, editable installs, and external working directories.
- Accepted the final `src/toetra` single-package layout and the
  responsibility-based internal namespace plan.
- Removed broad private-package aggregate exports and the historical IR2
  `nodes` shim; internal imports now target concrete private modules.
- Added `make ci-local`, a complete non-Ruff local gate for Windows hosts where
  Smart App Control blocks Ruff's unsigned native executable.
- Normalized the repository test tree under `tests/`, separated input
  fixtures from golden outputs, consolidated IR2 test locations, and moved
  reusable test builders and helpers under `tests/support/`.
- Renamed the Hypothesis implementation tree to `tests/property_based/` and
  standardized point-binding fixture names.

### Fixed

- Amended the frozen public and repository contract gates for P28.1 so the
  exact installed `toetra` entry point and private `_cli` subsystem are
  accepted without changing the nine-symbol Python facade or JSON v6.
- Named the regression route explicitly throughout onboarding and public demos,
  exposed its scalar `target[point]` observable in first-use examples, and
  removed the overloaded `Classification` label from regression examples.
- Prevented `session.print()` and the copied quickstart from failing on legacy
  Windows console encodings by selecting the equivalent ASCII report rendering.
- Removed an exact duplicate NNF end-to-end test and corrected misspelled
  mutation-module filenames.
- Tightened the public-facade and former-identity repository contracts.

## [1.0.0rc3] - 2026-07-26

### Changed

- Renamed the Python distribution and sole public import namespace to `toetra`.
- Renamed the specification extension, grammars, parser entry points, examples,
  demos, fixtures, and documentation to the Toetra Specification Language
  identity and `.toetra`.
- Advanced JSON reporting to schema v6 under the canonical
  `toetra.verification-report` and
  `toetra.verification-report-collection` identities.
- Renamed software provenance fields and build override to `toetra_version`,
  `toetra_build_id`, and `TOETRA_BUILD_ID`.
- Migrated numeric-compatibility, encoder, semantic-target, Miova artifact,
  replay, HTML, text, and default report identifiers to `toetra.*`.
- Renamed the repository, documentation URLs, review bundle, and release
  metadata to the canonical Toetra identity.

### Compatibility

- Verification semantics and the regression/classification routes remain those
  accepted in `1.0.0rc2`.
- The legacy `forml` import namespace and `.forml` extension are intentionally
  unsupported because no project-controlled stable release used them.
- JSON schema v5 remains historical; current reports use schema v6.

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
