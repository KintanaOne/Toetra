# Quantified Point Bindings

> Status: Implemented and normative  
> Scope: Ordered `forall` and `exists` point bindings

## Syntax

```toetra
forall x0
exists candidate
forall x0, x1
```

Unicode aliases may normalize to the same internal quantifier kinds. A binder list expands left to right:

```toetra
forall x0, x1
```

is equivalent to:

```toetra
forall x0
forall x1
```

Ordered clauses preserve lexical nesting:

```toetra
forall original
exists counterfactual
=> ...
```

Indentation is optional and never determines meaning.

## Binding rules

Each binder introduces one exact `PointSymbol` and one lexical frame. Toetra
preserves the source identifier through semantic validation, IR1, IR2,
model-semantic lowering, backend symbols, reports, and replay.

- duplicate names in one list are rejected;
- shadowing is rejected in V1;
- a binder may not collide with a global anchor;
- an inner clause may reference visible outer points;
- unknown explicit points are never aliased to a visible one.

## References

With one eligible point, shorthand is allowed:

```toetra
forall x0
=> age >= 18 and target <= 0.8
```

This resolves to `x0.age` and `target[x0]`. With several eligible points, explicit qualification is required.

Domains always use explicit subjects:

```toetra
forall x0, x1
with domain(
    x0.age: [18, 90],
    x1.age: [18, 90]
)
=> ...
```

## Restrictions

A single `where` clause restricts the innermost binder and may reference all points visible there:

```toetra
forall x0
exists x1
where x1.a >= x0.a
=> ...
```

Its semantic lowering depends on the innermost quantifier:

```text
forall → restriction implies property
exists → restriction and property
```

## Execution profile

Homogeneous chains are executable with the current Z3 profile:

```text
forall, forall
exists, exists
```

Alternating chains are represented exactly, reported in IR2 requirements, and rejected before translation because the initial backend does not support native quantifier alternation. They are never flattened into an unsound free-variable query.
