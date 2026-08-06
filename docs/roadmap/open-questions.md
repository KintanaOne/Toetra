# Open questions

> **Status:** Active from the `1.0.0rc4` evaluation candidate
>
> **Rule:** this page records unresolved choices in the order they are expected
> to matter; it does not announce implemented support

The public routes, nine-symbol Python facade, current language meanings, and
as-built pipeline are already decided. Their authorities are the
[public V1 profile](../public-v1-profile.md), accepted contracts and ADRs, and
the [implementation status matrix](../architecture/status-matrix.md).

## During public evaluation

### Observation and feedback

How much observation is sufficient before the candidate can be considered for
a stable release? Which external reports require a new release candidate, and
which usability improvements can wait until after V1?

### Installation evidence

Which operating-system, Python, wheel, source-distribution, and documentation
journeys must be reproduced outside the development repository before stable
publication?

### Solver execution guarantees

The runtime already enforces a 30,000 ms default backend timeout, while the
advanced internal execution policy can opt out with `timeout_ms=None`. Which
cancellation and resource-limit controls are enforceable enough to become
public guarantees, and which must remain best-effort evidence?

## Before stable `1.0.0`

### Stable-release acceptance

Which unresolved soundness, security, provenance, packaging, documentation, or
compatibility defects block `1.0.0`? Which release artifacts and rollback
evidence are mandatory before publication?

## After V1

### Next model route

Which additional model family creates the most useful verifiable behavior while
keeping its encoder and numeric contract auditable: another affine family,
trees, ensembles, or a small neural profile?

### Framework versus mathematical family

When should Toetra add another framework adapter for an existing semantic
family instead of adding a new model family? Framework popularity alone is not
evidence that a sound end-to-end route exists.

### Preprocessing boundary

Which preprocessing operations can be reconstructed symbolically, which should
be represented as verified contracts, and which must remain explicit
preconditions supplied by the user?

### Second backend

Which concrete property or model route justifies a backend beyond Z3? A second
backend should add a needed capability or trust boundary, not merely exercise
the registry abstraction.

### Numeric semantics

Which routes require bit-vector or floating-point reasoning rather than the
current exact-real abstraction with explicit compatibility evidence?

### Extension surface

When have the internal registries been exercised by enough independent
extensions to justify a stable third-party plugin API or scaffolding command?
Freezing that surface after one backend or one model family would be premature.

### Validation ecosystem

Which compiler and runtime invariants should be promoted first into Miova
mutation campaigns, and which higher-level orchestration decisions belong
outside Toetra itself?

## Decisions already made

The following questions are closed for the current V1 profile:

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
- independent timing for repository exposure, CLI adoption, and stable release;
- the initial CLI command surface (`validate`, `inspect`, `verify`, `replay`,
  and `init`), process statuses, stream ownership, diagnostic formats, and
  artifact behavior defined by the
  [CLI and automation contract](../contracts/cli-automation-contract.md);
- ownership boundaries for model families, framework adapters, and backends;
- canonical, CI-checked public documentation snippets.

The sequence in which these decisions were delivered is preserved in the
[project history](../history/roadmaps/index.md).
