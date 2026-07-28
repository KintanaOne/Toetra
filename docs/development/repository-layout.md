# Repository layout

The repository separates installable code, executable demonstrations,
documentation, automation, and verification assets by responsibility:

```text
src/toetra/     installable library and small package resources
demo/           complete executable user and engineering scenarios
docs/           public, internal, historical, and planning documentation
scripts/        repository automation grouped by operational intent
tests/          unit, integration, end-to-end, property-based, fixture, and golden assets
```

## Installable code and examples

Only `src/toetra/` is installed. The `src/toetra/examples/` package contains
small resources required by installed examples, not complete training or review
workspaces.

Complete scenarios belong under `demo/`. They may include datasets, notebooks,
training code, policies, and ignored local artifacts. Generated models and
reports must not be committed beside immutable inputs.

## Repository scripts

Automation is grouped under one of four packages:

```text
scripts/ci/          local and hosted validation entry points
scripts/docs/        generated documentation tooling
scripts/release/     distribution, installation, and review-bundle tooling
scripts/repository/  source-tree identity and layout checks
```

The repository root of `scripts/` contains only its package initializer. New
one-off migration scripts should not remain after the migration is complete.

## Documentation lifecycle

The implementation roadmap and open questions remain under `docs/roadmap/`.
Delivered plans move to `docs/history/roadmaps/`, where they remain useful as
engineering evidence without appearing to describe pending work.

ADRs and contracts remain authoritative regardless of roadmap location.

## Extension guides

Built-in extension work starts from the
[extension architecture](extensions.md), then follows the dedicated path for a
[model family](adding-model-family.md), a
[framework adapter](adding-framework-adapter.md), or a
[backend](adding-backend.md). The paths are separate because mathematical model
meaning, framework integration, and backend execution have different owners and
soundness obligations.

## Frozen boundary

The executable invariants and change-control rules for this frozen layout are
defined by the [repository contract](../contracts/repository-contract.md).
