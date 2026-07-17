# Scope IR

> Status: Implemented point-aware compatibility projection

## Purpose

`ScopeIR` carries the canonical point context from semantic validation into IR1 and IR2. Its semantic source of truth is not the historical `kind` string but the structured fields:

```text
ScopeIR
├── points
├── binders
├── domain
├── restriction
├── selected/default point metadata
├── source/sugar provenance
└── compatibility fields: kind, variables, quantifier
```

## Points

Every point is represented by an exact point binding with name, binding kind, lexical depth, generated/source status, schema, and provenance where applicable. Domain constraints and scalar references point to these identities rather than reconstructing them from strings.

## Binders

`binders` preserves source expansion order and quantifier kind. A grouped binder is expanded left to right. Alternation remains visible to IR2 requirements.

## Domain and restriction

Domains contain point-owned interval or finite-set constraints. `restriction` remains separate from the user assertion so universal refutation and existential satisfaction can be built soundly.

Natural `Linf` neighborhoods are lowered to ordinary point-feature inequalities before backend translation.

## Compatibility fields

`kind`, `variables`, and the singular `quantifier` accessor remain for older consumers and one-point displays. They are derived views only:

- they must not decide semantic validity;
- they must not choose an input point;
- they must not flatten ordered binders;
- they must not define backend capability.

## Invariants

- all explicit point references resolve exactly;
- point order is deterministic and follows source declaration/binder order;
- short references exist only after unambiguous semantic resolution;
- indexed targets carry a structured model evaluation;
- legacy provisional source forms cannot create hidden point bindings.
