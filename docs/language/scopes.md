# Point Bindings and Property Contexts

> Status: Implemented and normative for the numeric-affine V1 profile  
> Scope: Point introduction, lexical visibility, restrictions, and user-facing sugar  
> Audience: DSL users, compiler contributors, backend authors, and test authors

## Core rule

FORML no longer assigns a property to one mutually exclusive semantic scope. A property is evaluated in a **composed point environment** containing:

- zero or more global anchors;
- an ordered chain of lexical quantifier binders;
- point-owned domains;
- an optional `where` restriction;
- zero or more model evaluations such as `target[x0]`.

`SemanticScope.POINTWISE`, `LOCAL`, `PAIRWISE`, and `QUANTIFIER` remain internal compatibility classifications for reports and older consumers. They are derived from the point environment and never decide meaning or backend eligibility.

## Point bindings

### Inline anchor

```toetra
anchor customer := {
    age: 42,
    income: 55000,
    debt_ratio: 0.31
}
```

The anchor is concrete, immutable, and expressed in the feature space consumed by the encoded model.

### Referenced anchor

```toetra
anchor customer := ref(
    key = "application_id",
    value = "APP-1842"
)
```

The runtime resolves this reference from, in order:

1. `anchor_resolver`;
2. `anchor_source`;
3. a compatible `dataset` fallback;
4. otherwise a structured missing-source error.

Lookup columns are metadata. They do not become model features unless the model schema explicitly declares them.

### Symbolic point

```toetra
forall applicant
```

```toetra
exists candidate
```

Several identifiers may be bound at once:

```toetra
forall x0, x1
```

This expands left to right to two nested universal binders. Ordered clauses preserve nesting:

```toetra
forall original
exists counterfactual
=> ...
```

Indentation is presentation only. Shadowing and collisions with global anchors are rejected.

## Domains and restrictions

`with domain(...)` constrains individual point features:

```toetra
forall applicant
with domain(
    applicant.age: [18, 90],
    applicant.income: [0, 200000]
)
=> target <= 0.8
```

`where` restricts admissible points or relates several points:

```toetra
forall lower, higher
where (
    higher.income >= lower.income
    and higher.age == lower.age
)
=> target[higher] <= target[lower]
```

The lowering is quantifier-sensitive:

```text
forall x where R => P  ≡  forall x: R -> P
exists x where R => P  ≡  exists x: R and P
```

The initial executable neighborhood is numeric `Linf`:

```toetra
forall perturbed
where perturbed in neighborhood(
    of = customer,
    metric = Linf,
    eps = 0.05
)
=> ...
```

## Model outputs

FORML V1 has one scalar target selected by the header. Brackets select the **input point**, not an output from a list:

```toetra
target[x0]
target[x1]
```

Repeated references to `target[x0]` reuse one `(model, x0, target)` evaluation. Different points create different evaluations and different backend symbols.

The short forms `target` and `age` are accepted only when exactly one eligible default point exists. FORML never silently picks the first or innermost point.

## Direct properties

An anchor can be used without an artificial left-hand scope:

```toetra
anchor customer := { age: 42, income: 55000 }

[BOUND]:
target[customer] <= 0.4 using Z3
```

## User-facing sugar

### `check_at`

```toetra
anchor customer := ref(key = "id", value = "R-42")

[BOUND]:
check_at customer
=> target <= 0.4 using Z3
```

`check_at` selects an already declared concrete anchor as the default point. It never declares a point.

### `at`

```toetra
anchor customer := { age: 42, income: 55000 }

[ROBUSTNESS]:
at customer with perturbed in neighborhood(
    metric = Linf,
    eps = 0.05
)
=> target[perturbed] <= target[customer] + 0.02 using Z3
```

This is deterministic sugar for a fresh universal candidate plus a natural neighborhood restriction. The explicit form and sugar use the same semantic, IR, ModelBridge, backend, reporting, and replay pipeline.

## Legacy migration

The provisional forms remain parseable only so FORML can emit stable migration diagnostics:

| Legacy form | V1 action |
|---|---|
| undeclared `check_at x0` | declare an inline/referenced anchor, then select it |
| `at x in neighborhood(...)` | use `anchor x := ...` and `at x with candidate in neighborhood(...)` |
| `x ~ x' ...` | use explicit `forall x0, x1` or `exists x0, x1` plus `where` |

They are never silently assigned the new meaning.

## V1 execution boundary

Implemented end to end:

- concrete inline and referenced anchors;
- homogeneous universal and existential binder chains;
- one or more points and model evaluations;
- numeric affine sklearn `LinearRegression` encoding;
- typed numeric domains and scalar arithmetic;
- `Linf` neighborhoods;
- grouped proof/counterexample/witness evidence;
- real-model replay for every referenced point.

Represented but capability-rejected:

- alternating quantifiers such as `forall x0` then `exists x1`.

Outside the V1 profile:

- arbitrary preprocessing reconstruction;
- categorical/symbolic backend sorts;
- multi-output models;
- nonlinear and rich model encoders;
- neighborhood metrics other than the implemented numeric-affine profile.
