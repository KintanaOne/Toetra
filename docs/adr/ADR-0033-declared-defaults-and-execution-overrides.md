# ADR-0033 — Separate Declared Defaults from Execution Overrides

> Status: Accepted
>
> Date: 2026-08
>
> Scope: DSL header defaults, runtime planning, compilation, provenance, replay,
> and CLI/API overrides

## Context

The Toetra grammar requires `model` and `target` declarations and permits an
optional `dataset`. MLOps workflows also need to reuse one property set against
candidate models, alternative output names, and different reference datasets.

Treating the header as immutable run configuration would force pipelines to
rewrite specifications. Treating CLI values as unrelated secondary
configuration would create conflicting sources of truth and incomplete
provenance.

## Decision

A specification header defines default values. Every invocation resolves a
separate immutable execution context using explicit CLI or Python arguments as
temporary overrides.

The declared AST is retained unchanged. An isolated effective AST view replaces
the model, target, and dataset header values before semantic validation and IR
construction. Model and dataset overrides select and fingerprint the effective
artifacts and rebuild the model schema. Model-evaluation IR therefore identifies
the effective model variant rather than the unused default.

Archived replay separates historical execution identity from current artifact
location: a moved file may be supplied as a locator, while the archived effective
header is recompiled for fingerprint comparison.

Validation, inspection, verification reports, artifact manifests, and replay
record or reconstruct both declared and effective values.

## Rationale

This design:

- makes formal policies reusable across candidate artifacts;
- avoids source-file mutation in CI and MLOps pipelines;
- gives target overrides real compiler semantics rather than cosmetic metadata;
- prevents stale schemas when model or dataset artifacts change;
- makes model-evaluation identity truthful for the selected variant;
- preserves archived identity when replay locates an artifact elsewhere;
- makes every override explicit and auditable;
- lets replay distinguish historical reconstruction from a new verification.

## Consequences

- `model`, `target`, and `dataset` options remain available on model-aware CLI
  commands.
- The runtime owns one resolution function and one execution-context model.
- Effective target changes participate in provenance and property identity.
- JSON v6 provenance gains an additive `execution_context` object.
- `replay --model` becomes optional because the DSL header is a valid default.
- `init` is the creation boundary: its model, target, and optional dataset
  arguments become declarations in the generated source, not temporary
  overrides.
- Future multi-output support must define how an effective target selects a
  concrete output port; this ADR does not claim that support today.

## Alternatives considered

### Require pipelines to rewrite `.toetra` files

Rejected because it damages provenance, portability, and policy reuse.

### Allow only model and dataset overrides

Rejected because output aliases or future output selections are legitimate
parameters of a reusable formal policy.

### Mutate the parsed AST in place

Rejected because declared source evidence and concurrent invocations would no
longer be isolated.

### Keep the declared model identity in effective compiler IR

Rejected because reports and model evaluations would name a default model that
was not actually verified. Replay instead preserves the archived effective
identity while allowing a separate current artifact locator.

## Impact on Toetra

The runtime gains an explicit declared/effective context boundary before model
resolution and compilation. The CLI remains an adapter: it supplies override
values, while the shared runtime applies and validates them for Python and
process callers alike.
