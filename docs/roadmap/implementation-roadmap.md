# Implementation roadmap

> **Status:** Active from the `1.0.0rc3` evaluation candidate
>
> **Scope:** public evaluation, the first automation surface, stable V1, and
> evidence-led capability expansion

This roadmap starts from the product that exists today. Delivered work belongs
in the [project history](../history/roadmaps/index.md); current support is defined
by the [public V1 profile](../public-v1-profile.md), not by future plans.

## Current position

`1.0.0rc3` is a source-installed evaluation candidate. Its public executable
profile includes:

- fitted single-output sklearn `LinearRegression`;
- direct fitted binary sklearn `LogisticRegression`;
- finite transformed numeric features and affine model encodings;
- homogeneous `forall` or `exists` point bindings;
- Z3 execution;
- text, JSON v6, HTML, Jupyter, records/DataFrame, provenance, and replay;
- reproducible distributions, clean-install checks, and a reproducible review
  bundle.

The repository structure, public Python facade, documentation baseline, error
boundary, reporting contract, contribution surfaces, licensing, and controlled
exposure procedure are already in place. These are current foundations rather
than future roadmap items.

The [implementation status matrix](../architecture/status-matrix.md) separates
code present in the repository from built-in and publicly guaranteed routes.

## Immediate — public evaluation

The next milestone is a controlled public repository exposure, without
presenting the candidate as a stable package release.

The remaining work is operational:

- expose the accepted commit and verify its public surfaces anonymously;
- confirm that the published repository matches the reviewed commit and review
  bundle;
- observe first-use, installation, documentation, security, and soundness
  feedback;
- correct release-candidate defects without widening the frozen V1 capability
  profile.

A GitHub Release is optional during this period and, if created, remains a
pre-release. PyPI publication and `1.0.0` are separate decisions.

## Next — CLI and automation

The process contract is now accepted in the
[CLI and automation contract](../contracts/cli-automation-contract.md) and
[ADR-0032](../adr/ADR-0032-cli-command-surface-and-application-boundary.md).
P28 implementation covers:

- equivalent installed `toetra` and `python -m toetra` entry points;
- `validate`, `inspect`, `verify`, `replay`, and `init` commands;
- stable exit-code meanings and strict stdout/stderr separation;
- machine-readable validation, inspection, diagnostics, and artifact manifests;
- predictable path, cancellation, and resource-policy behavior outside the
  source checkout;
- clean-install, Windows/Linux, container-job, and CI integration evidence.

The CLI remains an adapter over shared application workflows. Compiler,
verification, reporting, and replay semantics stay owned by the library rather
than being duplicated beneath the command-line layer. `compile` and `serve` are
reserved but deferred because they require, respectively, a versioned compiled
artifact or a separately secured network-service contract. This work may
justify another release candidate, but it does not by itself trigger the stable
release.

## Then — stable `1.0.0`

Stable V1 follows public observation and acceptance of the automation boundary.
The release milestone includes:

- a final clean-checkout, metadata, provenance, and licensing audit;
- deterministic wheel, source distribution, and review bundle;
- wheel and source-distribution installation across the accepted compatibility
  matrix;
- demonstrations and documentation built against release artifacts;
- publication rehearsal, checksums, release notes, and rollback evidence;
- the final transition to `1.0.0`.

This is a hardening milestone, not a late feature window. No calendar date
overrides a soundness, security, provenance, installation, or reproducibility
failure.

## Later — capability expansion

Post-V1 work will be selected from concrete user and integration evidence.
Candidate directions include:

- additional sklearn model families with auditable encoders;
- preprocessing-aware contracts and pipeline reconstruction;
- another framework adapter for an already-supported mathematical family;
- a second backend when it supplies a capability Z3 cannot;
- categorical, multi-output, or nonlinear reasoning;
- stronger property-based and Miova mutation campaigns;
- runtime monitoring and higher-level orchestration.

These are directions, not support promises. A model detector, schema
introspector, enum value, experimental encoder, or backend prototype does not
create a public route.

## How a capability becomes public

Model-family semantics, framework integration, and backend execution remain
separate extension responsibilities. A route becomes public only when all of
the following agree:

1. schema and observable semantics;
2. model-family lowering and formal encoding;
3. capability and numeric-compatibility policy;
4. backend translation and execution;
5. reporting, provenance, and replay;
6. unit, contract, end-to-end, clean-install, and release tests;
7. public-profile, reference, and release documentation.

Contributor entry points are documented in the
[extension architecture](../development/extensions.md), with dedicated guides
for a [model family](../development/adding-model-family.md),
[framework adapter](../development/adding-framework-adapter.md), and
[backend](../development/adding-backend.md).
