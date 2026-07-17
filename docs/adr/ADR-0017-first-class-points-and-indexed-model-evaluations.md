# ADR-0017 — Use First-Class Points, Lexical Bindings, and Point-Indexed Model Evaluations

> Status: Accepted and implemented — Patch 15 closed  
> Date: 2026-07  
> Scope: DSL points, anchors, quantifier nesting, scope semantics, ModelBridge evaluations, runtime results

## Context

FORML currently represents evaluation context through mutually exclusive scope forms such as `check_at`, `at`, pairwise syntax, and a single-variable quantifier. That model is sufficient while a property refers to one implicit input and one implicit model output, but it becomes ambiguous as soon as a specification needs any combination of:

- a concrete anchor and a symbolic perturbation;
- two independently quantified points;
- nested quantifiers;
- several evaluations of the same model;
- explicit comparison between model outputs at different points;
- replay of a multi-point witness or counterexample.

The current ModelBridge path also assumes one selected input entity and one global model output symbol. With two points, a single `_model.<target>` symbol cannot distinguish:

```text
model(x0)
model(x1)
```

The language therefore needs a stable distinction between:

1. a **point**;
2. the **binding** that introduces that point;
3. restrictions and relations involving points;
4. the **evaluation of the model at a point**;
5. the unique scalar target produced by that evaluation in the V1 profile.

This decision must be made before extending `at`, `check_at`, pairwise properties, anchors, or nested quantifiers, because it affects every compiler and runtime boundary.

## Decision

FORML will treat points as first-class semantic symbols.

A property is evaluated in a composed lexical environment containing point bindings, domains, restrictions, relations, and model-output references. The environment replaces the assumption that a property belongs to one exclusive semantic scope kind.

### 1. Point bindings

A point is introduced by exactly one binding.

The initial binding kinds are:

| Binding kind | Surface form | Semantic nature |
|---|---|---|
| Inline anchor | `anchor x0 := { ... }` | concrete, immutable |
| Referenced anchor | `anchor x0 := ref(...)` | concrete after runtime resolution |
| Universal binder | `forall x0` | symbolic |
| Existential binder | `exists x0` | symbolic |
| Runtime-provided anchor | public API binding to a declared anchor | concrete, immutable |

A point identifier must not be inferred from spelling conventions such as a prime suffix. Its role comes from its binding.

### 2. Global anchor declarations

Anchors are declared in the program body before properties.

Inline form:

```forml
anchor x0 := {
    age: 42,
    income: 55000,
    debt_ratio: 0.31
}
```

Referenced form for the initial single-source profile:

```forml
anchor x0 := ref(
    key = "customer_id",
    value = "C-1842"
)
```

The initial profile receives at most one anchor source from the runtime. A future named `source` argument remains possible but is not required by this decision.

Runtime source selection follows this precedence:

1. an explicit custom `anchor_resolver`;
2. an explicit `anchor_source`;
3. the compatible `dataset` artifact already supplied for model/schema introspection;
4. otherwise, a structured missing-source failure.

Reusing `dataset` is an ergonomic fallback, not a merger of responsibilities. Model introspection still owns the expected model schema, while anchor resolution still owns business-row lookup. An explicit resolver or source always overrides the fallback.

When the reused dataset contains lookup or provenance columns that were not consumed by the model, those columns MUST NOT be promoted to model features. For sklearn estimators, `feature_names_in_` is the authoritative ordered input contract when available; the dataset supplies dtypes and nullability for those named inputs only. A model without named-input metadata retains dataset inference and therefore requires a compatible dataset or an explicit schema/source split when extra metadata columns are present.

Anchor values are expressed in the feature space consumed by the encoded model. General preprocessing reconstruction remains outside the V1 scope.

### 3. Multiple binders and nesting

A quantifier may bind several identifiers:

```forml
forall x0, x1
```

This is syntactic sugar for left-to-right nesting:

```forml
forall x0
forall x1
```

Quantifier clauses may be nested by sequence:

```forml
forall x0
exists x1
with domain(...)
where ...
=> ...
```

The source order is semantically significant. Indentation is optional presentation only and must not affect parsing.

Shadowing is forbidden in the V1 target language. A point identifier may not be rebound while an outer binding with the same name is visible.

### 4. Point-indexed target references

FORML V1 keeps one scalar model output selected by the header declaration:

```forml
target := RiskScore
```

The language does not introduce a list of outputs.

Instead, brackets on `target` select the input point at which that unique output is evaluated:

```forml
target[x0]
target[x1]
```

The conceptual meaning is:

```text
output of the current model evaluated at x0
output of the current model evaluated at x1
```

The compiler must create distinct evaluation identities for distinct points and reuse the same evaluation identity for repeated references to the same `(model, point)` pair.

### 5. Implicit target and feature references

The short forms remain user-friendly when they are unambiguous:

```forml
target
age
```

They are valid only when semantic resolution identifies exactly one eligible default point.

| Eligible points | Short reference behavior |
|---:|---|
| 0 | reject: no evaluation point |
| 1 | resolve to that point |
| 2 or more | reject: ambiguous point |

The compiler must never choose the innermost point or the first declared point silently when several candidates are visible.

Domain subjects remain explicitly qualified:

```forml
x0.age: [18, 90]
```

### 6. Direct assertions

A property may contain a direct assertion without an artificial scope prelude when all referenced points are already declared:

```forml
anchor x0 := { age: 42, income: 55000 }

[BOUND]:
target[x0] <= 0.4 using Z3
```

The legacy `scope => assertion` shape therefore becomes one property form rather than the only property form.

### 7. Restrictions and neighborhoods

`where` introduces a restriction on quantified points.

Natural neighborhood syntax is normative:

```forml
forall x1
where x1 in neighborhood(
    of = x0,
    metric = Linf,
    eps = 0.05
)
=> (target[x1] - target[x0] <= 0.02)
   and (target[x0] - target[x1] <= 0.02)
```

The semantic lowering depends on the quantifier bound by the restriction:

```text
forall x where R => P  ≡  forall x: R -> P
exists x where R => P  ≡  exists x: R and P
```

With an ordered chain, the single `where` clause restricts the innermost binder and may reference all points visible there. Alternating chains preserve that bounded meaning even when the selected backend cannot yet execute them.

A neighborhood is a structured relation that lowers into ordinary logical and arithmetic constraints. It is not a separate semantic universe.

### 8. `check_at` as anchor selection sugar

`check_at` is retained for user-facing readability:

```forml
anchor baseline := { ... }

[BOUND]:
check_at baseline
=> target <= 0.4
```

It selects an already declared concrete anchor as the default point for the property. It does not declare the anchor and does not invent its values.

### 9. `at` as local universal sugar

`at` is retained as a user-friendly local verification form:

```forml
anchor x0 := { ... }

[ROBUSTNESS]:
at x0 with x1 in neighborhood(
    metric = Linf,
    eps = 0.05
)
=> (target[x1] - target[x0] <= 0.02)
   and (target[x0] - target[x1] <= 0.02)
```

It desugars to:

```forml
forall x1
where x1 in neighborhood(
    of = x0,
    metric = Linf,
    eps = 0.05
)
=> (target[x1] - target[x0] <= 0.02)
   and (target[x0] - target[x1] <= 0.02)
```

`at` therefore:

1. requires `x0` to be a declared anchor;
2. introduces `x1` as a fresh universally quantified point;
3. relates `x1` to `x0` through the neighborhood;
4. does not create a distinct semantic scope kind after desugaring.

Existential adversarial search remains explicit through `exists` rather than overloading `at` with a quantifier option.

### 10. Pairwise properties

Pairwise is treated as a derived classification of a property that uses two related points, not as a primitive binding or an implicit existential meaning.

Universal pairwise property:

```forml
forall x0, x1
where R(x0, x1)
=> P(x0, x1)
```

Its refutation query searches for:

```text
exists x0, x1: R(x0, x1) and not P(x0, x1)
```

Existential pair search remains expressible directly:

```forml
exists x0, x1
where R(x0, x1)
=> P(x0, x1)
```

The current mandatory `x ~ x'` naming convention is not part of the target core language.

### 11. Model evaluation identity

The semantic and IR identity of a model evaluation is:

```text
(model identity, point identity)
```

For an affine model, two referenced points produce two constraints:

```text
target[x0] = w · x0 + b
target[x1] = w · x1 + b
```

The coefficients are shared; the input and output symbols are distinct.

The ModelBridge must no longer select one input entity implicitly from a scope.

### 12. Quantifier execution profile

The language and IR must represent ordered nested binders, including alternation.

The initial executable V1 profile is required to support homogeneous chains that can be lowered to the current quantifier-free verification strategy:

```forml
forall x0, x1
exists x0, x1
```

Alternating chains such as:

```forml
forall x0
exists x1
```

must preserve their meaning through the front-end and IR. A backend without the required capability must reject them through a structured capability diagnostic before solver execution. They must never be flattened into an unsound free-variable query.

### 13. Runtime and replay

Results must preserve point identity and evaluation identity.

A multi-point witness or counterexample must be representable as:

```text
points
├── x0
│   ├── feature values
│   └── target[x0]
└── x1
    ├── feature values
    └── target[x1]
```

Replay must evaluate the real model independently at every referenced point and compare each concrete output with its formal output.

## Rationale

This decision separates concepts that were previously conflated:

```text
point
≠ binding
≠ relation
≠ model evaluation
≠ model output name
```

It provides one semantic core for pointwise checks, anchored local robustness, monotonicity, pairwise comparison, existential witness search, and future nested quantification.

The language remains user-friendly because `target`, `check_at`, `at`, and `neighborhood` are preserved as concise forms. Their behavior is nevertheless defined by deterministic lowering into the same explicit core.

## Consequences

### Positive

- Multiple evaluations of the same model become unambiguous.
- Anchors and symbolic points can coexist in one property.
- Quantifier order and lexical visibility become explicit.
- Pairwise and local properties share the same semantic machinery.
- ModelBridge constraints can be generated per referenced point.
- Results and replay can preserve complete multi-point evidence.
- User-friendly syntax remains available without creating independent semantic paths.

### Negative

- Scope handling must be redesigned across AST, semantic binding, IR1, IR2, ModelBridge, backend naming, runtime results, and replay.
- Existing tests and demonstrations using implicit `at`, `check_at`, or `x ~ x'` semantics must be migrated.
- Default-point resolution becomes a semantic validation responsibility.
- Alternating quantifiers require explicit capability gating.
- Referenced anchors require a runtime resolver boundary.

## Alternatives considered

### Keep mutually exclusive scope kinds

Rejected because an anchored, quantified, relational property belongs to several categories simultaneously.

### Keep one global model output symbol

Rejected because it cannot represent two evaluations of the same model without conflating their outputs.

### Use `model(x0)` function syntax

Rejected as the primary user syntax because the current language already exposes the output through `target`. `target[x0]` extends that vocabulary while preserving the single-output V1 model.

### Require explicit point qualification everywhere

Rejected because concise `target` and bare feature references are safe when exactly one default point exists.

### Make indentation define quantifier nesting

Rejected because it would make the grammar indentation-sensitive and create unnecessary parser complexity. Source order is sufficient.

### Remove all user-facing sugar

Rejected because FORML is intended to remain accessible to users expressing behavioral properties, not only to compiler contributors.

### Treat pairwise as nested `exists`

Rejected at the source-language level because most pairwise guarantees are universal. Double existential quantification is the refutation query for a universal pairwise property, not its declared meaning.

## Compatibility and migration

FORML is pre-V1. This ADR defines the target language contract and does not require permanent backward compatibility with provisional scope syntax.

Migration should prefer deterministic desugaring where meaning is preserved. Provisional forms whose meaning is ambiguous or incompatible may be rejected with migration diagnostics.

This ADR supersedes the following target assumptions while preserving their implemented historical value:

- the single-variable initial-scope limitation in ADR-0013;
- mutually exclusive target scope categories;
- a global unindexed `target` output symbol;
- implicit creation of a primed perturbation entity;
- the mandatory `x ~ x'` pair naming convention;
- `check_at` as an unresolved concrete point declaration.

## Impact on FORML

### Grammar

The grammar must add global anchor declarations, binder lists, ordered binder chains, indexed target references, direct assertions, `where`, natural neighborhood restrictions, and the revised `at`/`check_at` forms.

### AST

The AST must preserve anchor declarations, ordered binders, optional point selection on target references, restrictions, and sugar nodes or equivalent source provenance.

### Semantic layer

The semantic layer must maintain a lexical point environment, validate exact bindings, forbid shadowing, resolve default points only when unique, and materialize point-indexed model-output references.

### IR1 and IR2

IRs must preserve point identity, quantifier order, restriction semantics, evaluation identity, and source quantifier intent.

### ModelBridge

Model constraints must be instantiated once per referenced `(model, point)` evaluation.

### Backends

Backend symbols may be flattened for solver use but must remain traceable to structured point and evaluation identities. Capability checks must reject unsupported quantifier alternation before translation.

### Runtime

The runtime must resolve referenced anchors, expose grouped point values and outputs, and replay every referenced model evaluation.

### Tests

The normative acceptance matrix is defined in:

```text
docs/testing/point-binding-evaluation-test-matrix.md
```

### Related documentation

- `language/points-anchors-and-evaluations.md`
- `language/scopes.md`
- `contracts/point-binding-and-evaluation.md`
- `testing/point-binding-evaluation-test-matrix.md`


## Implementation closure

Patch 15.12 completed this decision end to end. The implemented source of truth is the composed point environment and the structured `(model, point, target)` evaluation identity. Exclusive semantic scope kinds and flattened output strings are compatibility projections only.

The parser retains the provisional undeclared `check_at`, legacy `at x in neighborhood(...)`, and `x ~ x'` branches solely to emit stable migration diagnostics. They are never silently interpreted under the accepted semantics.

The numeric-affine V1 profile now includes runtime anchor resolution, one affine equation per requested point, point-aware Z3 symbols, grouped JSON v2/text/HTML evidence, and real-model replay for every referenced evaluation. Alternating quantifiers remain represented and capability-rejected before translation.
