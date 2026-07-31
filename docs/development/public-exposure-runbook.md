# Controlled public exposure runbook

This runbook closes P27.5 without coupling repository visibility to a package
publication or stable release. It does not create a GitHub Release, publish to
PyPI, add the P28 CLI, or declare the P29 stable `1.0.0`.

## 1. Select the immutable candidate

Use the complete canonical clone and fetch every reachable ref:

```bash
git fetch --all --tags --prune
git status --short
git rev-parse --is-shallow-repository
git rev-parse HEAD
git rev-parse origin/main
git ls-files '*.patch'
```

The status and patch-file listing must be empty, the clone must not be shallow,
and the two commits must be identical. Record that full commit as the accepted
exposure commit.

## 2. Run the final local gates

```bash
make public-snapshot-check
make public-history-check
make public-collaboration-check
make outside-in-check
make review-bundle
```

Keep `dist/toetra_review_bundle.zip` unchanged through the exposure operation.
Its embedded manifest must name the accepted clean commit.

Review the complete
[GitHub settings checklist](public-collaboration-and-workflows.md). Do not copy
secret values or private findings into the public evidence.

## 3. Change repository visibility

In the GitHub repository settings, change only the canonical
`KintanaOne/Toetra` repository visibility from private to public. Reconfirm the
repository name before accepting GitHub's warning.

Do not create or publish a package, tag, release, deployment, or CLI as part of
this operation. A GitHub Release remains optional and, if created later during
P27, must be marked as a pre-release.

## 4. Verify anonymously

Use a signed-out browser or private window to confirm the repository, README,
license, commercial-licensing route, issues, issue forms, security policy,
Actions results, and documentation site are visible. Recheck the
owner-controlled settings after the visibility change. GitHub may label the
PolyForm license as `NOASSERTION` or omit a detected-license badge; the
authoritative checks read the exact `LICENSE` file and package metadata.

Then run the credential-free automated probe:

```bash
make public-surface-check
```

The command disables Git credential helpers for its remote read, checks that
public `main` points to the accepted commit, validates GitHub's anonymous
repository metadata, reads critical files from that exact commit, checks the
issues and security surfaces, verifies the documentation site, and binds the
result to the review-bundle SHA-256. It writes only non-sensitive evidence to
`dist/p27-public-exposure-evidence.json`.

## 5. Record and observe

The P27 closure record contains:

- exposure time in UTC;
- accepted full commit;
- review-bundle SHA-256;
- successful snapshot, history, collaboration, outside-in, and anonymous
  surface checks;
- completed GitHub settings review;
- any deliberately accepted residual limitation;
- confirmation that PyPI, the P28 CLI, and stable `1.0.0` remain deferred.

P27 enters observation after this record is reviewed. Only soundness, security,
provenance, installation, materially misleading documentation, or material
usability defects reopen the candidate. Feature expansion remains outside P27.

## Stop conditions

Stop the exposure or return the repository to private visibility if:

- public `main` differs from the accepted commit;
- a secret, private artifact, or unresolved license issue appears;
- anonymous access or the security-reporting path is unavailable;
- an untrusted pull request receives write permission or a secret;
- any required durable gate fails.

Visibility rollback does not erase public clones or disclosures. Revoke any
exposed credential before rewriting history or attempting another exposure.
