# Public collaboration and workflow settings

This page records the source-controlled and repository-hosted controls required
by P27.3. It does not create a release or widen the V1 product boundary; the
separate Pages workflow publishes only the reviewed static site.

The separate `publish-pypi.yml` workflow prepares manual package publication
from `main` after the complete reusable CI. Publication remains pending.
See [PyPI publication](pypi-publication.md) for the one-time setup and explicit
release procedure.

## Source-controlled controls

The repository provides:

- `CONTRIBUTING.md` and a pull-request checklist;
- `SECURITY.md` with a private reporting route;
- structured issue forms for defects, documentation, and post-V1 proposals;
- a contributor-licensing boundary that accepts public feedback but does not
  merge outside code or documentation before an explicit contributor
  agreement;
- read-only pull-request CI with immutable action references;
- a separate, main-branch-only GitHub Pages deployment with immutable action
  references and the minimum Pages permissions;
- weekly Dependabot checks for pinned GitHub Actions.

The durable check is:

```bash
make public-collaboration-check
```

It rejects missing community files, mutable external action references,
write-capable workflow permissions in pull-request CI, secret use, privileged
untrusted-code triggers, publication commands, and checkout credential
persistence. The Pages workflow is checked separately: it can write only the
Pages deployment token, runs from `main` or manual dispatch, and never runs on
pull requests.

The PyPI exception is confined to its manual main-only workflow: only its
`publish` job receives `id-token: write`, uses the `pypi` environment, and waits
for the full reused CI. Its archives come from that same run, with identity and
checksum checks before upload. Permanent tokens and secret references remain
forbidden. The check rejects triggers or permissions that bypass these gates.

The CI workflow triggers on pushes to `main` and all pull requests. It preserves
Linux quality checks on Python 3.11/3.12, builds reproducible distributions once,
and transfers the wheel and sdist to eight Ubuntu/native-Windows installation
jobs covering both Python versions and both formats. Each job uses the same
isolated installed-package journey and fails on compatibility errors or checkout
mutations. Artifact download fails on a digest mismatch. Demonstrations and the
reproducible review bundle remain in the build job. The reusable CI has no
publication permission, and the GitHub Pages workflow is unchanged. See the
[release engineering contract](../contracts/release-engineering.md#automatic-installation-matrix)
for the matrix and reproduction links.

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

- [ ] Default workflow permissions are read-only. Pages alone has `pages: write`;
      OIDC write permission is restricted to Pages and the protected PyPI job.
- [ ] The `pypi` environment accepts only `main`; review requirements and
      self-review settings match the maintainer's intended release process.
- [ ] GitHub Actions cannot create or approve pull requests.
- [ ] The action allowlist includes only the reviewed GitHub actions and the
      pinned `pypa/gh-action-pypi-publish` action required for package publication.
- [ ] No repository or environment secret is available to pull-request CI or
      the Pages deployment.

### Main-branch protection

- [ ] Force pushes and branch deletion are blocked.
- [ ] Required checks cover both Linux quality jobs, the distribution/bundle job,
      and all eight Ubuntu/native-Windows, Python 3.11/3.12, wheel/sdist installation jobs.
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
no publishing identity, and no write permission. The landing page and
documentation publication is a separate, explicitly authorized main-branch
operation with a dedicated Pages environment.

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
