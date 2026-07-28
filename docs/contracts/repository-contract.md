# Repository contract

> **Status:** Frozen for `1.0.0rc3`
>
> **Scope:** repository and package structure through the V1 release

## Purpose

This contract freezes the structural boundaries established before the
documentation freeze. It prevents UX or release work from depending on another
implicit package or repository migration before V1.

## Canonical roots

```text
src/toetra/     the only installable Python package
tests/          verification assets and test support
demo/           complete executable scenarios
docs/           public, internal, historical, and planning documentation
scripts/        CI, documentation, release, and repository automation
```

The repository must not contain top-level `toetra`, `dsl`, `model`, `forml`,
`test`, or `examples` source trees.

## Installable package

Setuptools discovers packages only below `src/` and includes only `toetra*`.
The direct children of `src/toetra/` are:

```text
_backends
_compatibility
_compiler
_language
_models
_provenance
_reporting
_runtime
examples
```

Only names listed by `toetra.__all__` form the supported V1 Python API. Private
`toetra._*` package initializers do not aggregate implementation symbols.

The wheel and source distribution package inventories must match the files under
`src/toetra/`. The wheel must not contain repository-only trees. Small installed
resources remain limited to the grammar and `toetra.examples` policy data.

## Repository-only assets

`tests/` separates executable tests, input fixtures, expected golden outputs,
and shared support code. Inputs do not live below golden directories and golden
outputs do not contain executable Python.

Complete user and engineering scenarios live below `demo/`. Installed examples
remain deliberately small package resources.

Automation lives in one of these packages:

```text
scripts/ci/
scripts/docs/
scripts/release/
scripts/repository/
```

The `scripts/` root contains no one-off implementation script.

Exactly two active planning documents live under `docs/roadmap/`: the
implementation roadmap and open questions. Delivered patch plans, including the
V1 implementation and documentation roadmaps, live under
`docs/history/roadmaps/` and do not describe pending work.

## Executable gates

```bash
make repository-check
make ci-local       # complete local gate except Ruff
make ci             # authoritative quality gate including Ruff
make demo-check
make release-check
make review-bundle-check
```

`make ci` and `make ci-local` are non-mutating. Formatting changes are made
explicitly with `make format`. Hosted CI remains authoritative for Ruff on hosts
where Windows Smart App Control blocks its unsigned native executable.

Release validation keeps the quality, public demonstration, distribution, and
review-bundle gates explicit. Distribution building requires a clean checkout.

## Change control

Before V1, changing a canonical root, public import boundary, installable package
inventory, or fixture/golden role requires:

1. an explicit architecture decision;
2. an update to this contract and its executable checker;
3. clean-install and distribution validation;
4. documentation and review-bundle validation.

UX and release-hardening work may exercise these boundaries but must not
silently reorganize them.
