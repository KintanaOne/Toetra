# Toetra Identity Migration Roadmap

> Status: Complete — delivered in `1.0.0rc3`
> Patch family: P23
> Baseline: `1.0.0rc2`
> Target: `1.0.0rc3`
> Governing decision: [ADR-0027](../adr/ADR-0027-adopt-toetra-as-canonical-identity.md)

## Goal

Migrate the complete public identity from FORML to Toetra without changing the
verification semantics stabilized in `1.0.0rc2`.

The migration covers human-facing names, install and import contracts,
specification files, machine-readable identifiers, documentation, release
artifacts and repository metadata. It deliberately excludes unrelated feature
work and internal package-layout redesign.

## Non-goals

P23 does not:

- add a new model family, backend, property or language construct;
- change the meaning of an existing verification result;
- move the internal `dsl` and `model` namespaces beneath `toetra`;
- introduce a compatibility package, import alias or dual file extension;
- create a new CLI merely to occupy the `toetra` command name.

## Patch sequence

### P23.0 — Decision and inventory

- accept ADR-0027;
- record the migration surfaces and ordering;
- verify the P22 canonical review bundle;
- keep the project at `1.0.0rc2`.

Exit criterion: the intended names, exclusions, compatibility policy and schema
version policy are unambiguous before code migration begins.

### P23.1 — Distribution and public Python facade

- replace the `forml` package facade with a regular `toetra` package;
- change the distribution name to `toetra`;
- migrate public imports, clean-install probes and packaging tests;
- remove `forml` from package discovery and type-checker roots;
- keep `dsl` and `model` as internal packages.

Exit criterion:

```python
from toetra import VerificationSession, VerificationStatus, verify
```

works from a clean wheel installation and `import forml` is not supported.

### P23.2 — Toetra Specification Language surface

- rename `.forml` specifications to `.toetra`;
- rename grammar files to `toetra_grammar.ebnf` and `toetra_grammar.lark`;
- rename public and internal parser helpers whose names encode the former
  identity, including `parse_forml_code`;
- migrate examples, fixtures, goldens, demos and notebook references;
- migrate Markdown code fences from `forml` to `toetra`;
- accept only `.toetra` at the public runtime boundary.

Exit criterion: every executable language sample and release demo uses the
Toetra Specification Language identity and `.toetra` extension.

### P23.3 — Persistent identifiers and report schema v6

- migrate `forml.*` JSON schema and evidence identifiers to `toetra.*`;
- advance `REPORT_SCHEMA_VERSION` from 5 to 6;
- update JSON schema tests, renderer tests, provenance fixtures and golden
  reports;
- document that v6 changes the canonical identity while preserving the intended
  report semantics.

Exit criterion: no current machine-readable artifact claims the former product
identity and schema v5 remains historical.

### P23.4 — Documentation, demos and repository metadata

- migrate README, architecture, contracts, language documentation, ADR wording,
  demos and generated documentation;
- update PyPI metadata, GitHub URLs, badges, MkDocs metadata and page labels;
- use **Toetra Specification Language** without promoting `TSL`;
- retain former-name wording only where historically necessary.

Exit criterion: a new user encounters one coherent Toetra identity from the
repository landing page through first verification.

### P23.5 — Release engineering and old-identity gate

- rename review bundles, temporary directories and generated artifacts;
- update distribution and release scripts;
- add a checked allowlist for necessary historical references;
- change the project version to `1.0.0rc3`;
- add release notes and changelog entries;
- run clean wheel, sdist and review-bundle validation.

Exit criterion: release gates fail on any unapproved `FORML`, `forml` or `.forml`
occurrence.

### P23.6 — Repository cutover and candidate publication

- rename the remote repository to `KintanaOne/Toetra`;
- update the local Git remote and verify GitHub Actions and Pages;
- rebuild artifacts from the renamed repository;
- publish `toetra==1.0.0rc3` only after the remote cutover is green.

Exit criterion: source, remote, documentation and published candidate all use
one identity.

## Cross-patch acceptance rules

Each patch must:

- remain independently reviewable;
- keep `make ci` green;
- avoid semantic or feature changes;
- update tests in the same patch as the contract they protect;
- use Bash commands in contributor instructions;
- finish with `git diff --check`.

The release-oriented checks are mandatory from the first patch that changes
packaging or artifact identity:

```bash
make release-check
make review-bundle-check
```

## Final acceptance scan

The final source-tree scan must be empty outside the explicit historical
allowlist:

```bash
rg -n 'FORML|forml|\.forml' \
  --glob '!docs/adr/ADR-0027-adopt-toetra-as-canonical-identity.md' \
  --glob '!docs/roadmap/toetra-identity-migration-roadmap.md' \
  --glob '!CHANGELOG.md'
```

The allowlist itself must be reviewed rather than expanded automatically.
