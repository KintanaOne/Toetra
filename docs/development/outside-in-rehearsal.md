# Outside-in public journey rehearsal

P27.4 validates the exact candidate commit from the perspective of a reader who
does not have the original development worktree. It does not publish the
repository, create a release, or modify Git history.

## Durable gate

Run the rehearsal only after committing the candidate and confirming that the
canonical clone is complete:

```bash
git status --short
git rev-parse --is-shallow-repository
make outside-in-check
```

The status must be empty and the shallow-repository check must return `false`.
The gate then:

1. records the exact source commit;
2. performs a new non-local clone into a temporary directory;
3. checks out that commit in detached-HEAD state;
4. creates a new Python environment;
5. follows the README installation, import, and quickstart commands literally;
6. requires exactly one `PROVED` and one `WITNESS` quickstart conclusion;
7. installs the documented development and documentation extras;
8. runs `make ci`, `make demo-check`, `make release-check`, and
   `make review-bundle-check`;
9. verifies that the candidate clone remains clean.

The temporary clone and environment are removed after the rehearsal. Dependency
installation may use the configured Python package index and can take several
minutes.

## Why this is a separate command

`make outside-in-check` invokes the existing CI and release gates from the
fresh clone. It therefore cannot be included in `make ci`, `make
release-check`, or `make review-bundle-check` without creating a recursive
validation loop.

The gate proves that committed source is sufficient for the documented journey.
It deliberately ignores editor configuration, local virtual environments,
untracked files, and imports from the original checkout.

## Deferred online checks

Before repository exposure, GitHub repository, issue, security, documentation,
and release URLs may not be anonymously reachable. P27.5 verifies those
surfaces after the accepted commit becomes public and records the exposed
commit plus the review-bundle digest.
