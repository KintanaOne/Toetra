# ADR-0004 — Normalize Enums and Vocabulary at Explicit Boundaries

> Status: Stabilizing  
> Date: 2026-06  
> Scope: Language vocabulary and type normalization

## Context

Toetra uses vocabulary values such as:

- property types,
- problem types,
- functions,
- comparison operators,
- metrics,
- quantifiers,
- backend names,
- data types.

These values may appear in different forms:

```text
z3
Z3
forall
∀
ROBUSTNESS
EnumProperty.ROBUSTNESS
```

Without explicit normalization, downstream layers may fail unpredictably.

## Decision

Toetra should normalize vocabulary values at explicit boundaries.

Recommended boundaries:

```text
Parser / Builder boundary
Builder / Semantic boundary
Semantic / IR boundary
IR / Backend boundary
ModelBridge / Semantic boundary
```

Each boundary should receive or produce canonical enum values.

## Rationale

Centralized normalization avoids duplicated ad-hoc conversions.

It also makes error messages clearer and makes Miova mutations easier to classify.

## Consequences

### Positive

- More predictable behavior.
- Fewer enum/string mismatch bugs.
- Easier property-based testing.
- Clearer contracts between layers.

### Negative

- Requires a dedicated normalization API.
- Existing code may need cleanup where enums and strings are mixed.
- Some grammar choices must be stabilized.

## Alternatives considered

### Let each layer normalize locally

Rejected because it duplicates logic and creates inconsistent behavior.

### Accept only one exact spelling everywhere

Rejected because the DSL should allow reasonable user-facing syntax, while internal layers should remain canonical.

## Impact on Toetra

Type normalization should become a documented P0 contract.

All future backend and ModelBridge integration work should rely on canonical values.
