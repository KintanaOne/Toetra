# ADR-0021 — Treat release engineering as a verified product contract

- **Status:** Accepted
- **Date:** 2026-07-19
- **Decision owners:** FORML maintainers

## Context

FORML can only claim a stable V1 if the source checkout, Python distributions and review bundle represent the same product. A green test suite inside a developer checkout is insufficient when:

- CI reformats or cleans files before checking them;
- the wheel omits the public `forml` package or grammar resources;
- an editable install hides missing distribution files;
- source bundles silently exclude notebooks, datasets or public modules;
- repeated builds produce unexplained artifact differences.

These failures do not change solver semantics, but they can make a correct engine impossible to install, reproduce or review.

## Decision

FORML adopts four independent release gates.

### 1. Non-mutating verification

`make ci` only checks repository state. Formatting and notebook cleanup remain explicit developer commands. Hosted CI verifies that the checkout is unchanged after every check.

### 2. Reproducible Python distributions

Wheel and source distribution builds use:

- pinned build-system versions;
- a stable `SOURCE_DATE_EPOCH`;
- deterministic archive ordering and metadata;
- two independent builds whose SHA-256 hashes must match.

The wheel and sdist are then checked for project identity, safe paths, public packages and required grammar data.

### 3. Clean-install contract

The built wheel is installed in a fresh virtual environment outside the repository. The probe imports the public `forml` API and packaged grammar resources with checkout paths removed from Python resolution.

An editable installation is not release evidence.

### 4. Complete review bundles

The review bundle generator includes tracked and non-ignored source files in deterministic order and fails when critical V1 artifacts are missing. Its embedded manifest records every file size and SHA-256 digest. Building the same source state twice must produce the same ZIP hash.

## Rationale

The gates deliberately separate different failure classes:

| Gate | Detects |
|---|---|
| non-mutating CI | checks that repair the checkout before passing |
| distribution contract | missing packages, package data or inconsistent metadata |
| clean-install probe | editable-install leakage and unusable wheels |
| review-bundle contract | incomplete or non-reproducible review snapshots |

No single gate substitutes for the others.

## Consequences

- Python 3.11 and 3.12 are both CI baselines.
- Build tooling is pinned separately from runtime dependencies.
- A release candidate cannot be accepted from an editable checkout alone.
- Review bundles include small data and notebook fixtures required by tests.
- Large serialized models remain excluded from review bundles unless explicitly promoted to required fixtures.
- Byte reproducibility is required for generated wheel, normalized sdist and review ZIP artifacts under the same source date epoch.

## Alternatives considered

### Keep one mutable `make ci`

Rejected because it can hide formatting and notebook hygiene failures.

### Test only `pip install -e .`

Rejected because editable installs do not prove wheel contents.

### Trust setuptools defaults

Rejected because package discovery and source-distribution inclusion rules can change independently of FORML's public contract.

### Keep ad hoc review ZIP scripts

Rejected because silent exclusions already produced an incomplete bundle that reported no missing critical paths.

## Impact on FORML

This ADR does not extend the DSL or verification engine. It makes the delivered artifact itself a verified FORML boundary and provides the build identity required by verification provenance.
