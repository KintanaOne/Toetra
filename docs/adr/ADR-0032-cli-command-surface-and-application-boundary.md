# ADR-0032 — CLI Command Surface and Application Boundary

> Status: Accepted
> Date: 2026-08
> Scope: P28 command set, process contract, and ownership boundaries

## Context

Toetra already has a complete source-to-report verification workflow, structured
public errors, JSON v6 reporting, provenance, backend-neutral execution policy,
and concrete replay attached to in-memory findings.

A CLI limited to a single `verify` command would expose less operational value
than the implementation can support. In particular, CI/CD and MLOps workflows
need to fail before solver execution, archive a resolved verification plan,
separate formal verification from later concrete replay, and create a safe first
specification without writing Python.

At the same time, exposing raw compiler stages or a network service would create
new compatibility and security commitments that the current architecture has
not accepted.

## Decision

P28 accepts five commands:

| Command | Responsibility |
|---|---|
| `validate` | stop at an explicit pre-execution boundary and report acceptance |
| `inspect` | describe the complete resolved execution plan without solving |
| `verify` | execute formal verification and emit reports/artifacts |
| `replay` | replay archived JSON v6 witness/counterexample evidence without solving |
| `init` | create and validate a model-aware smoke specification |

The exact process behavior is governed by the
[CLI and automation contract](../contracts/cli-automation-contract.md).

`compile` and `serve` are reserved but deferred.

### Application boundary

The CLI is implemented beneath `toetra._cli`, but verification semantics do not
live there.

```text
_cli command adapters
    ↓
_runtime application workflows
    ↓
compiler / ModelBridge / compatibility / backend / reporting / replay
```

- `verify` continues to delegate to the accepted high-level verification
  workflow;
- `validate` and `inspect` share an extracted pre-execution planning workflow;
- `replay` shares report loading, provenance matching, pre-execution task
  reconstruction, and the existing replay engine;
- `init` shares model loading/introspection and executable validation.

Command adapters own only argument parsing, path resolution, stream selection,
atomic writes, signal translation, and process-status mapping.

The nine-symbol public Python facade is not widened merely to implement P28.
The new application workflow may remain private until independent Python demand
justifies a separate public API decision. This does not permit duplicate logic:
private application services are shared by all CLI commands.

## Validation depth

Three validation levels are accepted:

```text
syntax     source → AST
semantic   syntax → model-aware IR1
executable semantic → translated backend query, no solver call
```

`inspect` requires the executable level so that it describes an actually
routable and translatable plan rather than a speculative partial plan.

## Replay boundary

`replay` consumes an archived JSON v6 report plus explicitly supplied source and
model artifacts. It validates provenance, reconstructs the matching compiled
task without solving, and then applies concrete replay.

It does not:

- trust paths embedded in a report;
- ignore fingerprint mismatch;
- rerun the solver;
- deserialize a private compiled cache;
- claim success when no evidence is replayable.

This design keeps replay useful for delayed MLOps checks while avoiding an
unstable serialized IR contract.

## Initialization boundary

`init` generates a syntactically and executably valid smoke specification based
on a supported model. It uses a deliberately tautological model-output or label
comparison and labels it as an integration smoke check.

It does not infer business thresholds, safety properties, robustness budgets,
or fairness requirements from data.

## Deferred commands

### `compile`

A meaningful `compile` command would create a portable executable artifact,
cache key, compatibility policy, versioned serialization format, and invalidation
rules. Dumping private AST/IR objects would accidentally freeze implementation
details without delivering that value.

The command remains deferred until Toetra accepts a compiled-artifact contract
for distributed or cached execution.

### `serve`

A meaningful `serve` command would create an HTTP/API product boundary with
model-upload security, isolation, resource governance, authentication,
concurrency, persistence, observability, and cancellation requirements.

Kubernetes, Airflow, Argo, Kubeflow, GitHub Actions, GitLab CI, and similar
systems can run the process CLI as a job. A daemon is not required to prove
MLOps integration.

## Consequences

### Positive

- CI can distinguish syntax, semantic, route, logical, and replay failures;
- pipelines can inspect and archive the exact intended route before solving;
- formal results remain JSON v6 instead of being wrapped in another success
  schema;
- delayed replay becomes possible without freezing IR2 serialization;
- onboarding gains a safe, model-aware first file;
- CLI code remains thin and independently testable;
- Toetra can run naturally as a container job before any network service exists.

### Negative

- P28 requires a pre-execution planning seam instead of calling `verify(...)`
  for every command;
- replay requires a strict JSON v6 reader and provenance/task matching;
- five new machine schemas must be governed: validation, inspection, replay,
  run manifest, and CLI diagnostics;
- signal, stream, and filesystem behavior add cross-platform tests;
- the process API becomes a new compatibility surface before stable `1.0.0`.

## Alternatives considered

### Ship only `verify`

Rejected because it forces pipelines to pay solver cost before detecting route
errors and offers no resolved-plan or delayed-replay workflow.

### Expose every internal compiler stage

Rejected because AST, IR1, IR2, and backend-native queries are private and not
accepted serialization contracts.

### Make `replay` rerun verification

Rejected because that is a new verification followed by replay, not replay of
archived evidence.

### Add `serve` for Kubernetes readiness

Rejected because job-style container execution is the smaller and safer MLOps
primitive. A service requires a separate threat model and operational contract.

### Expand the public Python facade immediately

Deferred. A private shared application seam is sufficient to keep CLI logic
thin. Public Python validation/inspection types can be accepted later from
independent usage evidence.
