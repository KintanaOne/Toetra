# Command-line interface

> `1.0.0rc4` implements `init`, `validate`, `inspect`, `verify`, and `replay` for both
> the installed `toetra` entry point and `python -m toetra`. The
> [Python API](../api-reference/index.md) remains available for embedded use.

## Goals

The Toetra CLI is designed for:

- local terminal verification;
- CI quality gates;
- container and Kubernetes jobs;
- Airflow, Argo, Kubeflow, GitHub Actions, GitLab CI, and similar orchestrators;
- archiving formal reports, provenance, and later concrete replay.

The accepted command set is:

```text
toetra validate
toetra inspect
toetra verify
toetra replay
toetra init
```

Current implementation status:

| Command | Status |
|---|---|
| `validate` | implemented |
| `inspect` | implemented |
| `verify` | implemented |
| `replay` | implemented |
| `init` | implemented |

The normative behavior is defined by the
[CLI and automation contract](../contracts/cli-automation-contract.md) and the
[execution override contract](../contracts/execution-overrides.md). The
application boundary is recorded in
[ADR-0032](../adr/ADR-0032-cli-command-surface-and-application-boundary.md),
while declared defaults and temporary overrides are recorded in
[ADR-0033](../adr/ADR-0033-declared-defaults-and-execution-overrides.md).

## Intended workflow

```text
model artifact + optional reference dataset
        ↓
optional toetra init policy.toetra --model ... --target ... [--dataset ...]
        ↓
toetra validate --level executable
        ↓
toetra inspect --format json
        ↓
toetra verify --format json --artifacts-dir artifacts/toetra
        ↓
pipeline gate on exit status
        ↓
optional delayed toetra replay of archived evidence
```

`validate` and `inspect` never invoke the solver. `verify` produces the formal
conclusion. `replay` validates archived JSON v6 provenance, reconstructs the
matching property tasks, and checks witness/counterexample evidence against a
concrete model without silently rerunning formal verification.

The model, target, and dataset declared in `.toetra` are defaults. Explicit CLI
values create a temporary effective context for one invocation, so the same
formal properties can be evaluated against compatible candidate artifacts and
output names without rewriting the policy file.

## Process statuses

| Status | Pipeline meaning |
|---:|---|
| `0` | accepted/successful/consistent |
| `1` | formal failure or replay inconsistency |
| `2` | formal or replay outcome is inconclusive |
| `3` | invalid usage, source, artifact, or configuration |
| `4` | unsupported route or technical runtime/filesystem failure |
| `5` | unexpected internal failure |
| `130` | interrupted |
| `143` | terminated where SIGTERM is supported |

A pipeline must choose whether `2` is allowed. Treating `UNKNOWN` as success by
accident is explicitly discouraged.

## Deferred surfaces

`compile` is deferred until Toetra has a versioned portable compiled-artifact
contract. `serve` is deferred until a network API, isolation, authentication,
resource governance, and model-upload threat model are designed.

Neither command is required to run Toetra as a robust MLOps job.

## Initialization contract

`toetra init` creates a deterministic integration smoke specification. It
requires an explicit model and target, writes an optional dataset declaration,
and validates the generated source at executable depth before publication. The
smoke property proves only that Toetra can introspect, compile, route, translate,
and verify the selected model wiring; it is not business or safety evidence.
