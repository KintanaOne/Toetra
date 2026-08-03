# ADR-0030 — Separate Public Exposure, CLI, and Stable Release

> Status: Accepted
> Date: 2026-07
> Scope: repository publication and the remaining path to `1.0.0`

## Context

After P26, Toetra has a green `1.0.0rc3` baseline with a frozen public Python
facade, reproducible distributions, clean-wheel probes, executable
demonstrations, and a reproducible review bundle.

Three remaining objectives have different risk and acceptance boundaries:

1. making the source repository safe and understandable to an external reader;
2. adding a process-level CLI for automation, CI/CD, and future orchestration;
3. hardening and publishing the stable `1.0.0` distribution.

Treating all three as one release patch would either delay useful public
exposure or force a new CLI and a stable-version commitment before real-world
observation.

## Decision

The remaining work is split into three independent projects:

| Project | Purpose | Version consequence |
|---|---|---|
| P27 | make the GitHub repository safe, truthful, and usable while public | remain on `1.0.0rc3` unless a defect requires another candidate |
| P28 | define and implement the CLI and automation contract | may justify a later release candidate; does not imply `1.0.0` |
| P29 | prove stable-release metadata, artifacts, publication, and rollback | contains the eventual stable release cut |

P27 changes repository visibility only after the
[public repository readiness contract](../contracts/public-repository-readiness.md)
is satisfied. Public GitHub visibility does not by itself:

- publish a package to PyPI;
- create a GitHub Release;
- declare the candidate stable;
- add a `toetra` entry point;
- widen the supported verification profile.

If a GitHub Release is created during P27, it is explicitly marked as a
pre-release and contains only artifacts built from the accepted public commit.

P28 owns the CLI contract. The accepted command surface and process behavior
are defined by the
[CLI and automation contract](../contracts/cli-automation-contract.md) and
[ADR-0032](ADR-0032-cli-command-surface-and-application-boundary.md). The CLI
remains an adapter over shared application workflows; command syntax, stream
behavior, machine-readable output, artifacts, and exit codes are accepted
before an entry point is published.

P29 owns stable-release hardening and the transition to `1.0.0`. No calendar
date overrides a soundness, provenance, security, installation, or
reproducibility blocker.

## Rationale

Repository publication is reversible at the visibility-setting level but
exposes every reachable public object immediately. It therefore needs
repository, history, legal, and communication checks rather than new product
behavior.

A CLI creates a separate public compatibility surface. It deserves its own
contract and observation rather than being hidden inside repository cleanup.

The stable version should follow actual use of the release candidate. Keeping
that decision in P29 allows feedback and personal experimentation to inform
confidence without reopening the frozen V1 semantics.

## Consequences

### Positive

- Toetra can leave the private workshop before the stable release is forced;
- public exposure, automation, and package publication each have binary gates;
- P27 cannot accidentally create an undocumented CLI contract;
- real-world observations can inform P28 and P29;
- the `1.0.0rc3` label remains truthful during the public observation period.

### Negative

- the path to `1.0.0` contains two additional explicit project boundaries;
- public users may initially install from source or attached pre-release
  artifacts rather than PyPI;
- repository settings and Git history require evidence outside the source
  snapshot.

## Alternatives considered

### Keep one release-hardening project

Rejected because it couples public visibility, a new automation surface, and
stable publication even though they have different failure modes.

### Add the CLI during public-repository preparation

Rejected because repository readiness must not become a feature window.

### Wait for `1.0.0` before making the repository public

Rejected because public observation of a clearly labelled release candidate is
useful evidence for the stable-release decision.

## Impact on Toetra

P27 may change documentation, repository policy, contribution surfaces,
workflow security, provenance records, and public-hosting configuration. It
must not change the language, supported model routes, proof semantics, JSON v6,
the Z3-only V1 backend, or the nine-symbol Python facade.

P28 and P29 begin from a P27 baseline only after the public repository has been
observed and any exposure blockers have been resolved.
