# Execution Override Contract

> **Status:** Implemented and accepted
>
> **Scope:** resolution of declared and effective model, target, and dataset
> values for Python and CLI verification workflows
>
> **Audience:** runtime, compiler, provenance, replay, CLI, and MLOps
> maintainers

## Purpose

A Toetra specification is a reusable formal policy with a default execution
context. One invocation may temporarily instantiate the same properties against
a different compatible model artifact, output name, or reference dataset.

The precedence rule is:

```text
explicit CLI or Python argument
    > declaration in the .toetra header
```

An override applies only to the current invocation. It does not rewrite the
source file or mutate the parsed declared AST.

## Declared and effective context

Every model-aware invocation resolves an immutable execution context containing:

```text
declared model / target / dataset
effective model / target / dataset
model / target / dataset override flags
```

The declared values are the exact header defaults. The effective values are the
ones used by the current run. Validation, inspection, verification, manifests,
and JSON v6 provenance expose both views.

## Model override

`--model` or `model=...` selects the concrete model artifact consumed by the
run. The effective model is loaded, introspected, encoded, and fingerprinted
from scratch. No schema or equations from the declared artifact may be reused.

The isolated effective AST receives the effective model reference before
semantic validation. Model-evaluation IR, reports, and property fingerprints
therefore identify the model variant that was actually selected, while the
declared reference remains available separately in provenance.

Archived replay preserves that historical effective identity. A later
`--model` value may act only as an artifact locator for a moved file; the
archived identity remains the one recompiled and compared against the archived
property fingerprint. Content fingerprints remain authoritative for the bytes.

## Target override

`--target` or `target=...` is a semantic override. It changes what the DSL token
`target` denotes for the current invocation.

The runtime:

1. validates the override as a non-reserved Toetra identifier;
2. creates an isolated effective AST view;
3. replaces model, target, and dataset header values in that view;
4. binds or aliases the effective model schema output to the same target name;
5. compiles that effective view through semantic validation, IR1, IR2, model
   lowering, routing, reporting, and replay.

The declared AST remains unchanged. The effective target participates in input
and property identity, so two runs with different targets cannot be confused in
provenance or replay.

Current built-in model routes expose one normalized output port. A target
override therefore renames that effective output binding. Future multi-output
routes may use the same contract to select a compatible output, but support is
not implied until their schema and lowering contracts are public.

## Dataset override

`--dataset` or `dataset=...` replaces the optional declared dataset for one run.
The effective dataset participates in:

- model-schema construction and dtype inference;
- feature and output metadata;
- referenced-anchor fallback when no dedicated anchor source is supplied;
- content-addressed provenance and replay reconstruction.

The effective schema is rebuilt after the override. A dataset override is never
treated as a cosmetic path change.

## Initialization boundary

`toetra init` runs before a specification exists. Its required model and target,
and optional dataset, are therefore written as declared defaults in the new
header. They are not recorded as execution overrides. The generated source must
validate at executable depth using only those declarations before it is
published atomically.

## Validation levels

`validate --level syntax` parses the specification and resolves the textual
execution context without loading override artifacts. Its result may therefore
show declared/effective values and override flags, but it does not claim that
the effective model, target, or dataset is semantically compatible.

`semantic` and `executable` consume the effective context and validate it at
their normal boundaries. Execution-policy options remain invalid below
`executable` because those options would otherwise be silently ignored.

## Replay

Archived replay reconstructs the effective historical context. The archived
effective target is reused automatically when `--target` is omitted. Model and
dataset options are optional because the specification header supplies defaults.
For a new report they define the effective execution context. During replay they
may locate moved artifacts, while the archived effective model, target, and
dataset identities remain authoritative for recompilation.

The reconstructed content fingerprints, effective target, schema, and property
fingerprints must match the JSON v6 archive. An override cannot be used to replay
an archived finding against a different context. Such a request is a new
verification, not replay.

## Failure rules

The invocation fails closed when:

- an override target is empty, malformed, or reserved;
- an effective artifact does not exist or cannot be introspected;
- effective features, output observables, anchors, or model semantics are
  incompatible with the properties;
- archived replay cannot reconstruct the same effective input identity.

No boundary may silently fall back from an explicitly supplied override to the
header default.

## Regression requirements

Tests must cover at least:

- declared values preserved without overrides;
- all three override flags and effective values;
- target rebinding from AST through IR1 and IR2;
- schema-only target rebinding without mutation of the caller's schema;
- model and dataset overrides rebuilding the effective schema;
- target changes affecting provenance identity;
- inspection and validation exposing declared/effective values;
- JSON v6 and run manifests recording the execution context;
- replay accepting header defaults and rejecting a mismatched effective context;
- installed-wheel execution of an overridden target.
