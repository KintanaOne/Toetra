# Public collaboration and workflow settings

This page records the source-controlled and repository-hosted controls required
by P27.3. It does not publish Toetra, create a release, or widen the V1 product
boundary.

## Source-controlled controls

The repository provides:

- `CONTRIBUTING.md` and a pull-request checklist;
- `SECURITY.md` with a private reporting route;
- structured issue forms for defects, documentation, and post-V1 proposals;
- a contributor-licensing boundary that accepts public feedback but does not
  merge outside code or documentation before an explicit contributor
  agreement;
- read-only pull-request CI with immutable action references;
- no `pull_request_target`, publication credential, deployment, or release job;
- weekly Dependabot checks for pinned GitHub Actions.

The durable check is:

```bash
make public-collaboration-check
```

It rejects missing community files, mutable external action references,
write-capable workflow permissions, secret use, privileged untrusted-code
triggers, publication commands, and checkout credential persistence.

## GitHub settings checklist

These controls live on GitHub and therefore require owner verification. Record
their final state in the P27 exposure evidence without copying secrets or
private findings.

### General and collaboration

- [ ] The default branch is `main`.
- [ ] Issues are enabled and show the repository issue forms.
- [ ] Private vulnerability reporting is enabled.
- [ ] The public contact identity and repository description are intentional.

### Actions

- [ ] Default workflow permissions are read-only.
- [ ] GitHub Actions cannot create or approve pull requests.
- [ ] Only GitHub-authored actions are allowed for the current P27 workflow, or
      an equally narrow allowlist is configured.
- [ ] No repository or environment secret is available to pull-request CI.

### Main-branch protection

- [ ] Force pushes and branch deletion are blocked.
- [ ] Required checks cover Python 3.11, Python 3.12, and the distribution job.
- [ ] Pull requests cannot merge while required checks fail.
- [ ] Any maintainer bypass is deliberate and recorded.

### Supply-chain and secret protection

- [ ] Dependency graph and Dependabot alerts are enabled.
- [ ] Dependabot security updates are enabled.
- [ ] Secret scanning and push protection are enabled when available.
- [ ] The weekly GitHub Actions version-update configuration is active.

## Pull-request trust boundary

The `pull_request` workflow executes contributor-controlled code, including
tests and build hooks. It therefore receives only a read-only token, no secrets,
no publishing identity, and no write permission. Publication remains a
separate, explicitly authorized future operation.

Opening a pull request does not grant Toetra the commercial relicensing rights
needed by its dual-licensing model. Until an explicit contributor agreement is
published and accepted, outside code and documentation pull requests are not
merged. Issues, reviews, reproductions, and proposals remain welcome.

Never replace this boundary with `pull_request_target` plus an untrusted
checkout. Never pass issue, pull-request, branch, or commit text directly into a
shell command.

## P27 closure

P27.3 source controls are complete when the collaboration gate and hosted
pull-request CI pass. The GitHub settings are rechecked immediately before and
after the visibility change by the
[P27.5 controlled exposure runbook](public-exposure-runbook.md).
