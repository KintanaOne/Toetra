# Repository structure

> **Status:** Delivered after the `1.0.0rc3` identity cutover

Once Toetra had its canonical identity, the repository was consolidated so the
documentation and release process could describe one stable structure.

## Canonical package layout

All installable code moved under `src/toetra/`. Former top-level implementation
trees were absorbed into private, responsibility-based namespaces for the
compiler, language, models, backends, runtime, reporting, provenance, and
numeric compatibility.

Setuptools discovery was restricted to the single `toetra` package family, and
grammar loading moved to packaged resources so parsing behaves consistently in
editable installs, wheels, source distributions, and external working
directories.

## Repository responsibilities

The remaining roots acquired explicit roles:

- `tests/` for executable tests, fixtures, golden outputs, and shared support;
- `demo/` for complete user and engineering scenarios;
- `scripts/` for CI, documentation, release, and repository automation;
- `docs/` for public reference, architecture, contracts, development guidance,
  planning, and history.

Private aggregate exports and obsolete compatibility shims were removed.
Large runtime modules were separated by responsibility without changing public
results or replay behavior.

## Frozen boundary

Repository, distribution, demo, and clean-install checks made the layout an
executable contract rather than a convention. The current rules are defined by
the [repository contract](../../contracts/repository-contract.md) and
[layout guide](../../development/repository-layout.md).
