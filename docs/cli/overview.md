# Command-line interface

> This page documents the intended process interface before implementation. The
> current release candidate is still used through the
> [Python API](../api-reference/index.md).

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

The normative behavior is defined by the
[CLI and automation contract](../contracts/cli-automation-contract.md). The
architecture decision is recorded in
[ADR-0032](../adr/ADR-0032-cli-command-surface-and-application-boundary.md).

## Intended workflow

```text
model artifact + policy.toetra
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
conclusion. `replay` checks archived witness/counterexample evidence against a
concrete model without silently rerunning formal verification.

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
