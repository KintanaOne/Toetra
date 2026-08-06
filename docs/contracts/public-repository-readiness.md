# Public repository readiness contract

> **Status:** Accepted for P27
>
> **Scope:** safe public exposure of the `1.0.0rc4` source repository

## Purpose

This contract defines the evidence required before the canonical Toetra GitHub
repository changes from private to public. It covers the source snapshot, the
reachable Git history, legal provenance, external-facing documentation,
collaboration surfaces, automation safety, and post-exposure verification.

Repository visibility is distinct from package publication and stable-release
acceptance. Passing this contract does not publish Toetra to PyPI and does not
change the version to `1.0.0`.

## Frozen product boundary

P27 must preserve:

- the nine-symbol `toetra.__all__` facade;
- the Parser → AST → semantic → IR1 → IR2 → backend pipeline;
- the accepted regression and direct binary-classification routes;
- JSON report schema v6;
- the Z3-only V1 backend profile;
- verification conclusions, numeric guarantees, provenance, and replay;
- the `src/toetra` single-package layout.

P27 does not add an installed CLI. CLI syntax, streams, exit codes, and
automation behavior belong to P28.

### P28.1 amendment

After P27 acceptance, P28.1 adds the installed `toetra` and `python -m toetra`
process entry points under the separate CLI automation contract. This additive
amendment does not retroactively change the evidence required for the P27 public
exposure decision.

## Acceptance evidence

### 1. Public snapshot hygiene

The exact commit selected for exposure must contain:

- no credentials, private keys, access tokens, secret-bearing configuration, or
  private environment files;
- no local absolute user paths, private work artifacts, patch files, build
  outputs, or unintended serialized models;
- no personal data beyond identities and contact addresses deliberately
  declared for public project use;
- no obsolete public product identity or misleading compatibility promise;
- a clean Git status and a reproducible review bundle for that commit.

Automated pattern checks are defense in depth, not proof that arbitrary secrets
are absent. Every finding requires human classification before exposure.

The durable snapshot check is:

```bash
make public-snapshot-check
```

It scans tracked filenames and textual content, freezes known third-party asset
digests, and fails on automated blockers without printing matched secret values.

### 2. Reachable Git history

The canonical clone, not a source bundle, must be inspected across every
reachable branch and tag. The inspection covers:

- credential and high-entropy secret history;
- deleted private configuration or binary artifacts;
- unintended names, addresses, paths, issue exports, datasets, or documents;
- stale branches and tags that would become public with the repository.

A secret found in history is revoked even if history is later rewritten.
History rewriting is a deliberate repository-owner operation performed before
public exposure, followed by a fresh-clone verification. The review bundle
cannot satisfy this gate because it contains no `.git` history.

After fetching every reachable branch and tag in a non-shallow canonical clone,
the history check is:

```bash
make public-history-check
```

The command lists refs and author/committer identities for deliberate human
review, then scans every reachable blob. It reports only rule identifiers,
object prefixes, and repository paths. Passing it is defense in depth; the owner
still classifies identities, refs, large or binary history, and any external
secret-scanner findings.

### 3. Legal and provenance boundary

The public commit must provide:

- the declared civil copyright holder and covered years for original Toetra
  source code and documentation;
- the accepted PolyForm Noncommercial 1.0.0 project license;
- the separate commercial-licensing route and contact;
- an accurate source-available claim, with no claim that Toetra is open source
  under the Open Source Definition;
- an intentional public author/contact identity;
- provenance, license, and required attribution for every third-party dataset,
  fixture, image, generated asset, or substantial copied source;
- confirmation that generated and vendored material may be redistributed;
- no claim that the project license overrides a third-party asset license.

An asset without a documented redistribution basis blocks public exposure.
The root `THIRD_PARTY.md` file is the public attribution registry. Asset-specific
documentation must link to it, and any separately licensed material must keep a
content digest so an unnoticed replacement cannot inherit an unrelated notice.

The root `COPYRIGHT.md` notice records the ownership claim and separates it
from third-party material. The reproducible review bundle binds that notice,
the exact Git commit, and every included file digest. An optional e-Soleau
deposit supplies independent dated evidence of that exact archive; it does not
create copyright or resolve competing ownership claims. Receipt and
restitution information remain private.

Until an explicit contributor agreement exists, outside code and documentation
contributions are not merged. Issues, reviews, reproductions, and proposals may
still be accepted without transferring code copyright.

### 4. External narrative and first use

An unfamiliar reader must be able to determine from the repository:

- what Toetra verifies and what it does not verify;
- that `1.0.0rc4` is a release candidate, not a stable release;
- which Python, model, framework, and backend routes are supported;
- how to install and run the first example from documented available artifacts;
- where the public API, limitations, release notes, and changelog live;
- how to report a defect or security concern.

Documentation must not claim that PyPI, GitHub Pages, issue tracking, or release
artifacts are available before those public surfaces actually exist.

### 5. Collaboration and automation safety

Before accepting untrusted public contributions:

- workflow permissions are least-privilege and explicit;
- pull-request workflows do not expose publication credentials or use a
  privileged untrusted-code path;
- publication remains a separate, protected, manually authorized operation;
- contribution, security-reporting, and issue-intake expectations are present;
- repository settings enable appropriate branch protection and security
  features for the public project.

Settings controlled by GitHub are recorded as manual evidence because source
tests cannot enforce them.

The source-controlled gate is:

```bash
make public-collaboration-check
```

The owner-settings checklist is maintained in
[Public collaboration and workflow settings](../development/public-collaboration-and-workflows.md).

### 6. Outside-in validation

The candidate public commit is validated without private checkout assumptions:

- clean clone or archive in a new directory;
- documented development installation;
- `make ci`, demonstrations, distribution checks, and review-bundle checks;
- README quick path followed literally;
- documentation built strictly and local links checked;
- repository and documentation URLs checked when they become reachable.

The durable clean-clone rehearsal is:

```bash
make outside-in-check
```

It targets the exact committed source state, creates a detached fresh clone and
new Python environment, follows the public first-use commands, runs all four
quality and release gates, and rejects any resulting checkout drift. Online
GitHub surfaces remain a P27.5 post-exposure check.

The credential-free post-exposure probe is:

```bash
make public-surface-check
```

It binds anonymous Git, GitHub metadata, critical public files, collaboration
surfaces, and the documentation site to the accepted commit and review-bundle
digest. The complete operation is defined by the
[controlled public exposure runbook](../development/public-exposure-runbook.md).

### 7. Controlled exposure and observation

The visibility change targets the exact accepted commit. Immediately afterward,
the project owner verifies anonymous access, the default branch, license,
README, issues/security contact, CI behavior, and documentation links.

GitHub repository visibility, a GitHub pre-release, PyPI publication, and the
stable `1.0.0` cut are four separate decisions:

| Decision | P27 consequence |
|---|---|
| make repository public | required outcome |
| create GitHub Release | optional; must be marked pre-release |
| publish to PyPI | deferred to the explicit publication plan |
| declare `1.0.0` stable | owned by P29 |

During observation, only soundness, security, provenance, installation,
misleading-documentation, or material usability defects reopen the candidate.
New capabilities remain outside P27.

## Blocking findings

Public exposure stops for any unresolved:

- valid or plausibly valid secret;
- private or personal material not intended for publication;
- missing redistribution right or attribution;
- unsafe public pull-request workflow;
- false installation, support, release, or security claim;
- failing durable gate;
- mismatch between the reviewed commit and the commit made public.

Cosmetic polish and future feature ideas do not block exposure unless they make
the public description materially misleading.

## Required record

P27 closes only when the repository records:

- the exposed commit and review-bundle digest;
- the confirmed declared copyright holder and any privately retained e-Soleau
  record;
- snapshot, history, provenance, documentation, and workflow audit outcomes;
- manual GitHub-setting checks;
- any accepted residual limitations;
- post-exposure anonymous-access verification.

Secret values and private findings must never be copied into that record.

## Relationship to later projects

The CLI and automation contract is implemented in `1.0.0rc4`. The stable
release milestone reuses the durable release gates, adds publication and
rollback evidence, and owns the eventual `1.0.0` cut.
