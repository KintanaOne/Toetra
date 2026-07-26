# P24 — Repository Final Polish Roadmap

> Status: Active — P24.0 baseline and layout decision
> Baseline: `1.0.0rc3`
> Target: repository and package layout frozen for P25–P27
> Governing decision: [ADR-0028](../adr/ADR-0028-src-based-single-package-layout.md)

## Goal

Finish the structural work required before documenting and releasing Toetra V1.
P24 removes remaining repository ambiguity, adopts the final Python package
layout, narrows the installed and exported surface, normalizes tests and
examples, and decomposes only modules with demonstrated responsibility overlap.

P24 does not add a model, framework, backend, property, language construct, or
verification semantic.

## Final target

The installable source tree is rooted at `src/toetra/` and publishes only the
`toetra` top-level package. Internal subsystems use private,
responsibility-based namespaces. Repository-only assets remain outside `src/`:

```text
src/toetra/     installable library and package resources
tests/          unit, integration, end-to-end, property-based, fixture, and golden assets
demo/           executable user and architecture demonstrations
docs/           public, internal, extension, and historical documentation
scripts/        CI, documentation, release, and repository tooling
```

## Patch sequence

### P24.0 — Baseline, decision, and hygiene guardrails

- accept ADR-0028 and record the complete P24 sequence;
- mark P23 as complete;
- remove known exact test duplication and correct misspelled paths;
- lock the exact public facade in tests;
- make historical-identity allowances line-specific rather than file-wide;
- add repository tests preventing duplicate test modules and known obsolete
  paths.

Exit criterion: the current post-P23 baseline remains green and the destination
layout is unambiguous before any large move begins.

### P24.1 — Canonical `src/toetra` migration

- move installable code directly to the responsibility-based namespaces defined
  by ADR-0028;
- update imports, package discovery, package data, typing configuration, scripts,
  demos, tests, and critical review-bundle paths;
- publish only the `toetra` top-level package;
- retain no `dsl` or `model` compatibility namespace.

Exit criterion: source, wheel, and source distribution expose only `toetra`, and
all existing verification behavior remains unchanged.

### P24.2 — Public and internal boundary hardening

- review every `__init__.py` and remove accidental aggregate exports;
- keep the supported V1 facade equal to `toetra.__all__`;
- make internal code import concrete private modules rather than broad package
  aggregators where practical;
- add clean-install probes proving obsolete top-level namespaces are absent.

Exit criterion: public imports are explicit, exact, documented, and protected by
executable contracts.

### P24.3 — Tests, fixtures, and golden normalization

- rename `test/` to `tests/`;
- consolidate duplicate IR and normalization locations;
- place reusable builders and helpers under `tests/support/`;
- separate input fixtures from expected golden outputs;
- standardize test, fixture, golden, and example names.

Exit criterion: every test asset has one clear role and one canonical location.

### P24.4 — Demo, documentation, and script organization

- consolidate complete user scenarios under `demo/`;
- retain only small installed resources under `src/toetra/examples/`;
- group scripts by CI, docs, release, and repository intent;
- move completed roadmaps into an explicit historical section;
- update MkDocs navigation and all path-sensitive checks.

Exit criterion: a contributor can infer the purpose of every top-level tree and
no example or script is orphaned.

### P24.5 — Targeted module decomposition

- split replay orchestration by model, evaluation, classification, and rendering
  responsibility;
- split binary-classification semantic lowering into focused components;
- separate HTML templates/styles only if the boundary is behavior-preserving;
- avoid line-count-driven changes to coherent backend and provenance modules.

Exit criterion: the identified oversized modules no longer mix distinct
responsibilities, with byte- or structure-equivalent public outputs where
applicable.

### P24.6 — Final repository contract

- reject obsolete identities and paths outside documented historical evidence;
- reject duplicate test modules and ambiguous fixture/golden placement;
- validate the exact wheel and source-distribution contents;
- run all CI, release, documentation, demo, and review-bundle gates;
- freeze the package layout consumed by P25 documentation.

Exit criterion: P25 can document the architecture without anticipating another
repository or import migration before V1.

## Cross-patch rules

Every patch must:

- preserve verification semantics and report schemas;
- remain independently reviewable;
- update code, tests, documentation, and path contracts together;
- use Bash commands in contributor instructions;
- finish with `make ci` and `git diff --check`;
- run `make release-check` and `make review-bundle-check` whenever package or
  artifact paths change.
