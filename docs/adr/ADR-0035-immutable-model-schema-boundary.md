# ADR-0035 — Make ModelSchema an Immutable Snapshot Boundary

> Status: Accepted
> Date: 2026-08
> Scope: ModelBridge, ModelSchema, Model IR construction, runtime rebinding

## Context

`ModelSchema` is shared by semantic validation, model encoding, compatibility,
provenance, replay, and the emerging Model IR construction path. Its former
representation exposed mutable dictionaries for features and metadata, while
`FeatureSchema` and `ModelSchema` themselves could also be reassigned.

A shallow copy of the outer metadata dictionary did not isolate nested lists,
dictionaries, or framework-owned numpy values. A caller, adapter, builder, or
runtime helper could therefore change the effective model contract after
validation and before lowering or replay.

That is incompatible with treating Model IR values as valid-by-construction
artifacts. A builder must consume one stable model-interface snapshot.

## Decision

`ModelSchema` is a frozen, immutable snapshot.

- `features` is an ordered `tuple[FeatureSchema, ...]`;
- `FeatureSchema` is frozen;
- `metadata` is an ordered `tuple[MetadataEntry, ...]`;
- nested metadata mappings and sequences are recursively detached and frozen;
- unsupported mutable/object metadata values are rejected at construction;
- lookup is exposed through read-only `features_by_name` and
  `metadata_by_name` views;
- reporting and provenance request a detached built-in copy through
  `metadata_as_dict()`;
- adapters accumulate mutable local state, then construct one schema;
- changes such as output rebinding or XGBoost enrichment construct a new schema
  with `dataclasses.replace` rather than mutating an existing instance.

Feature order remains part of the normalized input contract. Metadata order is
preserved for deterministic equality and representation, but generic metadata
does not become computational authority. ADR-0034 continues to require
computation-defining parameters to migrate into typed Model IR fields.

## Rationale

The snapshot boundary guarantees that every consumer observes the same model
interface and evidence. It also prevents source framework arrays and caller
dictionaries from retaining mutation channels into normalized Toetra state.

Tuples make order and immutability explicit. Named read-only views preserve
ergonomic validation and lookup without reintroducing mutable ownership.

## Consequences

### Positive

- Model IR builders receive a stable schema input.
- Feature/coefficient alignment cannot change after introspection.
- Provenance and replay cannot observe later caller mutations.
- Schema equality and hashing are deterministic for normalized values.
- XGBoost enrichment and runtime output rebinding make state transitions
  explicit.

### Negative

- Internal callers must use `feature_names`, `features_by_name`,
  `metadata_by_name`, or `metadata_as_dict()` instead of dictionary mutation.
- Metadata is limited to recursively normalizable scalar, sequence, and
  string-keyed mapping values.
- Rebinding creates a new small schema object.

These costs are acceptable because `ModelSchema` is a private contributor
interface, not part of Toetra's public Python API.

## Alternatives considered

### Keep dictionaries and freeze only the dataclass

Rejected because a frozen dataclass containing mutable dictionaries is not
transitively immutable.

### Use `MappingProxyType` over caller dictionaries

Rejected as the canonical storage because the original dictionary could still
be mutated and nested values would remain mutable. A transient read-only lookup
view is acceptable only over already detached immutable feature values.

### Deep-copy on every consumer boundary

Rejected because it distributes ownership rules, adds repeated work, and still
allows mutation between consumers.

## Impact on Toetra

The ModelBridge output becomes a trustworthy snapshot boundary:

```text
framework model + optional dataset
        |
        v
mutable adapter-local extraction
        |
        v
immutable ModelSchema snapshot
        |
        +--> semantic validation / compatibility / replay
        |
        +--> Model IR builder --> immutable Model IR
```

This ADR strengthens ADR-0008 and provides the stable construction boundary
used by the affine Model IR runtime migration accepted in ADR-0034.
