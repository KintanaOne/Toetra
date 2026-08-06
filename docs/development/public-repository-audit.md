# Public repository audit

This procedure implements P27.1 for the exact `1.0.0rc4` candidate selected for
public exposure. It does not publish the repository, create a GitHub Release,
publish to PyPI, add a CLI, or change the stable-version decision.

## Evidence boundaries

Two different checks are required:

| Scope | Command | What it can prove |
|---|---|---|
| tracked public snapshot | `make public-snapshot-check` | automated filename, content, local-path, identity, serialized-artifact, and third-party-provenance rules for the selected worktree |
| every reachable Git blob | `make public-history-check` | the same strong content/path rules across local branches, remote refs, and tags in a complete clone |

Neither command proves that an arbitrary secret pattern is impossible. They are
defense-in-depth gates around an explicit human review. Findings never render
the matched value; secret material must not be copied into issues, commits,
review bundles, or audit records.

## Public snapshot

Run from the clean commit proposed for exposure:

```bash
git status --short
make public-snapshot-check
make review-bundle-check
```

The check rejects:

- sensitive filenames and private-key containers;
- strong credential and private-key text patterns;
- local Windows, macOS, or Linux user-home paths;
- non-reviewed public email addresses;
- patch, serialized-model, database, build, distribution, and generated-site
  artifacts;
- large tracked files requiring explicit review;
- missing or changed third-party material without matching provenance.

The intentionally public project identity is
`KintanaOne <KintanaOne@proton.me>`, as declared in `pyproject.toml`. Changing
that identity requires updating the audit allowlist deliberately.

## Third-party material

The root `THIRD_PARTY.md` notice records every redistributed third-party asset
known at P27.1. The UCI processed Cleveland dataset is
separately licensed under CC BY 4.0; Toetra's PolyForm Noncommercial license
does not relicense it.

The snapshot gate freezes both the repository copy digest and the notice
markers. A changed digest blocks exposure until the source, transformation,
license, attribution, and new digest have been reviewed.

UCI describes the distributed data as having patient names and
social-security numbers removed and replaced with dummy values. The repository
does not add identities or medical claims to those records.

Runtime dependencies declared in `pyproject.toml` are installed from their own
distributions and are not vendored into this repository. Test fixtures, golden
reports, specifications, notebooks, and generated documentation currently have
no identified third-party payload beyond the registered Cleveland dataset.

## Reachable history

The review bundle contains no `.git` directory and cannot close this gate. Use
the canonical clone:

```bash
git fetch --all --tags --prune
git status --short
git rev-parse --is-shallow-repository
make public-history-check
```

The shallow-repository answer must be `false`. Review every printed:

- local, remote, and tag ref;
- author and committer identity;
- suspicious historical path;
- strong credential-pattern finding;
- local absolute path;
- large or binary historical blob.

The automated history command scans deleted content whenever its blob remains
reachable from a branch or tag. It does not modify history.

If a real or plausible secret is found:

1. revoke or rotate it before any cleanup;
2. identify every reachable ref containing it;
3. decide explicitly whether history rewriting is required;
4. perform rewriting only from the canonical repository-owner workflow;
5. force-update the intended refs;
6. discard the audit clone and repeat the checks from a fresh complete clone.

Do not record the secret value. Record only the finding class, affected scope,
remediation, and the final accepted commit.

## P27.1 acceptance record

P27.1 is complete only after the repository owner records:

- snapshot audit result and reviewed commit;
- review-bundle SHA-256 for that commit;
- complete-history audit result;
- reviewed branch, remote-ref, and tag inventory;
- reviewed author/committer identities;
- third-party asset and redistribution decision;
- remediation of every blocker, without secret values.

The final visibility change and post-exposure anonymous checks remain P27.5.
