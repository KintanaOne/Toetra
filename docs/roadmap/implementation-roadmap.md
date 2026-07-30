# Implementation roadmap

> **Status:** Active after the `1.0.0rc3` documentation freeze
>
> **Scope:** remaining V1 stabilization and evidence-led post-V1 expansion

This roadmap starts from the implementation that exists. It does not redefine
the [public V1 profile](../public-v1-profile.md), accepted contracts, or the
nine-symbol Python facade.

## Current baseline

The implemented route is:

```text
.toetra source + model artifact
→ CST → ProgramNode AST → semantic validation
→ VerificationTask IR1 → model-semantic lowering → NNF
→ VerificationTaskIR2 + assumptions
→ BackendRoute → backend-private translation → VerificationResult
→ VerificationReport + provenance + concrete replay
```

The public release candidate supports:

- fitted single-output sklearn `LinearRegression`;
- direct fitted binary sklearn `LogisticRegression`;
- finite transformed numeric features and affine model encodings;
- homogeneous `forall` or `exists` point bindings;
- Z3 execution;
- text, JSON v6, HTML, Jupyter, records/DataFrame, provenance, and replay.

The [implementation status matrix](../architecture/status-matrix.md) separates
code present in the repository from built-in and publicly guaranteed routes.

## Remaining V1 sequence

### P26 — User and developer experience

P26 improves the boundaries users already encounter without widening the
verification profile:

- parser and semantic diagnostics;
- unsupported model, property, framework, and backend messages;
- consistent report presentation and failure ownership;
- clean-install and first-use feedback;
- error-path tests across the public `verify(...)` workflow.

Changes to error wrapping must preserve the distinction between compilation
failure, capability rejection, backend failure, and a logical result such as
`COUNTEREXAMPLE` or `UNKNOWN`.

P26.0 accepted the public failure classification and structured diagnostic
contract in
[ADR-0029](../adr/ADR-0029-public-verification-failure-boundary.md). P26.1
normalizes syntax, builder, and semantic failures while preserving their
internal ownership. P26.2 normalizes specification, model, and reference-dataset
artifacts plus model detection and introspection, while distinguishing invalid
artifacts from loaded but unsupported model integrations. P26.3 normalizes
model-encoder, model-semantic, numeric-compatibility, and backend-routing
failures while preserving the difference between incomplete configuration,
unsupported routes, and technical integration failures. P26.4 normalizes
runner lookup, backend translation, backend execution-policy, and technical
execution failures while preserving timeout, resource, cancellation, and
solver-unknown outcomes as reportable `UNKNOWN` results. P26.5 aligns terminal
text, HTML/Jupyter, records/DataFrame, and JSON v6 around one conclusion,
execution context, numeric trust boundary, evidence, provenance, and diagnostic
contract without changing JSON v6. P26.6 makes the public quickstart copyable
outside the repository, executes it against the clean-installed wheel, and
verifies both public notebooks from the repository root and their own
directories. P26 is complete.

### P27 — Public repository readiness

P27 makes the `1.0.0rc3` GitHub repository safe, truthful, and useful to an
external reader without forcing the stable release:

- **P27.0 — exposure acceptance freeze:** separate repository visibility, CLI,
  package publication, and stable release; accept the
  [public repository readiness contract](../contracts/public-repository-readiness.md);
- **P27.1 — snapshot, history, and provenance audit:** inspect credentials,
  private data, reachable Git history, author identity, licenses, datasets, and
  redistribution evidence;
- **P27.2 — public narrative and first use:** make README, installation,
  positioning, limitations, and release-candidate status truthful from outside
  the private checkout;
- **P27.3 — collaboration and workflow safety:** add contribution, security, and
  issue-intake surfaces and harden untrusted pull-request automation;
- **P27.4 — outside-in rehearsal:** clone or extract the exact candidate in a
  clean location and follow the public journey literally;
- **P27.5 — controlled exposure:** make the accepted commit public, verify the
  public surfaces anonymously, and record the evidence.

P27 keeps `1.0.0rc3` unless a release-candidate defect requires a later
candidate. A GitHub Release is optional and, if created, remains a pre-release.
PyPI publication and the stable version are separate decisions.

### P28 — CLI and automation contract

P28 defines a thin process-level adapter over the public Python workflow for
terminal use, CI/CD, and future orchestration. It owns:

- the installed `toetra` entry point and command grammar;
- stable exit-code meanings;
- stdout/stderr separation and machine-readable output;
- path and configuration behavior outside the checkout;
- CI integration examples and clean-install probes.

No compiler, verification, or reporting semantics live in the CLI. P28 may
justify another release candidate, but it does not force `1.0.0`.

### P29 — Stable release hardening

P29 turns the publicly observed release candidate into a publishable stable V1:

- final clean-checkout and metadata audit;
- deterministic wheel, source distribution, and review bundle;
- wheel and sdist installation across the accepted compatibility matrix;
- demonstrations and documentation built against release artifacts;
- publication rehearsal, checksums, changelog, release notes, and rollback
  evidence;
- the final transition to `1.0.0`.

P29 is a release-hardening phase, not a late feature window.

### `1.0.0`

The stable release is cut only after P27 public observation, the accepted P28
automation boundary, and all P29 durable gates pass from a clean checkout. No
calendar date overrides a soundness, security, provenance, installation, or
reproducibility failure.

## Post-V1 capability expansion

Post-V1 work is selected from concrete user and integration evidence. Candidate
directions include:

- additional sklearn model families with auditable encoders;
- preprocessing-aware contracts and pipeline reconstruction;
- another framework adapter for an already-supported mathematical family;
- a second backend when it provides a capability Z3 cannot supply;
- categorical, multi-output, or nonlinear reasoning;
- stronger property-based and Miova mutation campaigns;
- runtime monitoring and higher-level orchestration.

These are directions, not support promises. A model detector, schema
introspector, enum value, experimental encoder, or backend prototype does not
create a public route.

## Expansion rule

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

## Historical plans

Delivered patch plans live under
[completed roadmaps](../history/roadmaps/index.md). They explain how the current
contracts were reached but do not define present support or pending work.
