# Open questions

> **Status:** Active after the `1.0.0rc3` documentation freeze
>
> **Rule:** this page records unresolved choices, not implemented support

The public routes, nine-symbol Python facade, current language meanings, and
as-built pipeline are already decided. Their authorities are the
[public V1 profile](../public-v1-profile.md), accepted contracts and ADRs, and
the [implementation status matrix](../architecture/status-matrix.md).

## Before `1.0.0`

### Solver execution controls

The runtime already enforces a 30,000 ms default backend timeout. The advanced
internal execution policy can opt out with `timeout_ms=None`. Which cancellation
and resource-limit controls are enforceable enough to report as guarantees, and
which must remain best-effort evidence?

### Stable-release acceptance

How long should the final release candidate soak, which external installation
scenarios are mandatory, and which documentation or packaging defects block
`1.0.0` even when the core solver tests remain green?

### CLI automation contract

Which command shape, stream guarantees, exit-code meanings, and artifact
behaviors form the smallest stable CLI for terminal use, CI/CD, and future
orchestration? The CLI must remain a thin adapter over the public Python
workflow rather than a second implementation of verification semantics.

## Post-V1 product questions

### Next model route

Which additional model family creates the most useful verifiable behavior while
keeping the encoder and numeric contract auditable: another affine family,
trees, ensembles, or a small neural profile?

### Framework versus mathematical family

When should Toetra add another framework adapter for an existing semantic
family instead of adding a new model family? Framework popularity alone is not
evidence that a sound end-to-end route exists.

### Second backend

Which concrete property or model route justifies a backend beyond Z3? A second
backend should add a needed capability or trust boundary, not merely exercise
the registry abstraction.

### Preprocessing boundary

Which preprocessing operations can be reconstructed symbolically, which should
be represented as verified contracts, and which must remain explicit
preconditions supplied by the user?

### Extension surface

When have the internal registries been exercised by enough independent
extensions to justify a stable third-party plugin API or scaffolding command?
Freezing that surface after one backend or one model family would be premature.

### Numeric semantics

Which routes require bit-vector or floating-point reasoning rather than the
current exact-real abstraction with explicit compatibility evidence?

### Validation ecosystem

Which compiler and runtime invariants should be promoted first into Miova
mutation campaigns, and which higher-level orchestration decisions belong
outside Toetra itself?

## Closed questions

The following are no longer open:

- regression and direct binary-logistic public routes;
- label and probability observables and their native decision boundary;
- point identity, anchors, homogeneous binders, reporting, and replay;
- the `src/toetra` package layout and nine-name public facade;
- separation of syntax acceptance, semantic validity, and executable support;
- public normalization into the three existing error families while retaining
  stable diagnostic codes, owning stages, optional context, and chained causes;
- cross-format reporting of logical conclusions, execution context, numeric
  trust, evidence, provenance, and diagnostics while retaining JSON v6;
- standalone first use from a copied quickstart and repository-notebook launch
  behavior from the root or notebook directory;
- separation of public repository exposure, the CLI automation surface, and the
  stable release into P27, P28, and P29;
- ownership boundaries for model families, framework adapters, and backends;
- canonical, CI-checked public documentation snippets.

Their implementation history is preserved under
[completed roadmaps](../history/roadmaps/index.md).
