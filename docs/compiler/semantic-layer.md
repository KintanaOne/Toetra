# Semantic Layer

> Status: Implemented and stabilized for Patch 15  
> Scope: AST to semantically annotated AST  
> Audience: compiler, IR, ModelBridge, backend, and runtime contributors

## Purpose

The semantic layer turns syntax into exact, typed identities. It answers:

```text
Which points exist, how were they bound, which references resolve to them,
and which model evaluation does every target expression denote?
```

## Pipeline

```text
AST
  → register global anchors
  → fork a point environment per property
  → expand ordered quantifier binders
  → validate domains and restrictions
  → select or reject a default point
  → resolve point features and target evaluations
  → canonicalize check_at / at / neighborhood sugar
  → attach semantic annotations
  → IR1
```

## Composed point environment

`PointEnvironment` is the semantic source of truth. It contains immutable global anchors and ordered `LexicalPointFrame` entries. Every `PointSymbol` records its exact binding kind, schema, provenance, and source span where available.

The old `SemanticScope` enum remains a derived compatibility projection. It must not be used to decide property validity, point visibility, quantifier meaning, or backend capability.

## Anchors

Inline anchors are validated against `ModelSchema`: unknown, duplicate, missing, or incompatible features are rejected. Referenced anchors preserve lookup metadata and are resolved by the runtime before IR2. Lookup keys need not be model features.

## Lexical binders

Binder lists expand left to right. Ordered clauses preserve nesting and quantifier kind. Shadowing, duplicate binders, collisions with anchors, and references to unknown points are rejected.

Alternation is semantically valid and preserved. Backend support is decided later by capabilities.

## Default-point resolution

Bare feature and target references use this exact rule:

| Eligible points | Result |
|---:|---|
| 0 | no-point error |
| 1 | resolve to that point |
| 2+ | ambiguity error |

Specification constants retain precedence over implicit feature names. Explicit `x0.feature` and `target[x0]` never depend on a default point.

## Model evaluation identity

Every accepted target reference resolves to a `ModelEvaluationIdentity`:

```text
(model identity, point identity, target name)
```

The registry interns repeated references to the same evaluation and distinguishes references at different points. Source target expressions without a resolved evaluation are rejected before IR1.

## Restrictions and sugar

The semantic layer keeps three related artifacts distinct:

- the source assertion;
- the source/canonical restriction;
- the verification body used by universal refutation or existential satisfaction.

`where` is lowered according to the innermost quantifier. `neighborhood(..., metric=Linf, eps=...)` becomes point-owned numeric inequalities. New `at` syntax becomes a generated universal binder plus that restriction. `check_at` selects a declared concrete anchor.

Legacy `at x in neighborhood(...)`, pairwise `x ~ x'`, and undeclared `check_at` are diagnostic-only parser branches and are rejected with stable migration messages.

## Property contracts

Property validation is expressed against the composed environment, not an enum matrix. For example, `FAIRNESS` currently requires at least two visible points. Other property families rely on their logical/typed expression and backend requirements.

## Output contract

IR1 receives:

- exact point bindings;
- ordered binders;
- point-owned domains;
- restrictions separate from assertions;
- point-indexed model evaluations;
- source provenance and sugar provenance.

No semantic consumer may reconstruct these identities from flattened strings.
