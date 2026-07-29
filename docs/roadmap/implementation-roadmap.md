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
contract without changing JSON v6.

### P27 — Release readiness

P27 turns the green release candidate into a publishable V1:

- final clean-checkout audit;
- deterministic wheel, source distribution, and review bundle;
- clean-wheel installation and public import probes;
- demonstrations and documentation built from the release artifact;
- changelog, release notes, compatibility statement, and rollback evidence.

P27 is a release-hardening phase, not a late feature window.

### `1.0.0`

The stable release is cut only after the durable gates pass from a clean
checkout and the release candidate has had enough time to expose documentation,
packaging, and usability defects. No calendar date overrides a soundness or
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
