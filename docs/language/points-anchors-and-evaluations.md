# Points, Anchors, and Model Evaluations

> Status: Implemented normative language specification  
> Scope: Point declarations, quantifier binding, restrictions, target indexing, and user-facing scope sugar  
> Priority: P0  
> Audience: DSL users, compiler contributors, backend authors, runtime authors, test authors

## Purpose

This document defines the target FORML language for properties that use one or more input points and one or more evaluations of the same model.

The core model is:

```text
point binding
→ point symbol
→ optional domain and relational restrictions
→ model evaluation at that point
→ target value for that evaluation
```

A point is not a model output. A quantifier is not a neighborhood. A neighborhood is not a scope kind. These concepts compose explicitly.

## Normative vocabulary

The keywords **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are used normatively.

| Term | Meaning |
|---|---|
| Point | A named model input entity such as `x0` or `candidate`. |
| Anchor | A concrete immutable point. |
| Symbolic point | A point introduced by `forall` or `exists`. |
| Binding | The declaration that introduces a point and defines its role. |
| Restriction | A condition limiting admissible valuations of quantified points. |
| Model evaluation | The application of the current model to one point. |
| Indexed target | The unique model target evaluated at a selected point, such as `target[x0]`. |
| Default point | The unique point selected for implicit feature and target references. |
| Sugar | User-facing syntax deterministically lowered into the explicit core language. |

## Program placement

Anchor declarations appear after the required header declarations and specification constants, and before property sections.

```forml
model := "credit_risk.joblib"
target := risk_score

max_delta := 0.02

anchor baseline := {
    age: 42,
    income: 55000,
    debt_ratio: 0.31
}

[BOUND]:
target[baseline] <= 0.4 using Z3
```

An anchor declaration is global to the specification. A property may use any globally declared anchor, subject to default-point ambiguity rules.

## Inline anchors

### Syntax

```forml
anchor <identifier> := {
    <feature>: <literal>,
    ...
}
```

Example:

```forml
anchor x0 := {
    age: 42,
    income: 55000,
    debt_ratio: 0.31
}
```

### Rules

An inline anchor:

- MUST declare a fresh point identifier;
- MUST be immutable;
- MUST use unqualified feature names inside its own block;
- MUST provide values compatible with the model input schema;
- MUST reject duplicate features;
- MUST reject unknown features;
- SHOULD be complete for all model input features in the V1 profile;
- MUST refer to the transformed feature space consumed by the encoded model.

The declaration above contributes concrete facts equivalent to:

```text
x0.age == 42
x0.income == 55000
x0.debt_ratio == 0.31
```

The compiler must nevertheless preserve the anchor as a structured point binding so that provenance and replay remain available.

### Invalid forms

```forml
anchor x0 := {
    x0.age = 42
}
```

The anchor block is a structured value, not an assertion block.

```forml
anchor x0 := {
    age: 42,
    age: 45
}
```

Duplicate features are invalid.

## Referenced anchors

### Initial single-source syntax

```forml
anchor x0 := ref(
    key = "customer_id",
    value = "C-1842"
)
```

The initial runtime profile receives at most one reference source. Therefore the DSL does not require a named `source` argument.

A future extension may add:

```forml
source = "validation"
```

without changing the meaning of the existing form.

### Resolution contract

The runtime selects the anchor lookup mechanism in this order:

1. explicit custom resolver;
2. explicit `anchor_source`;
3. compatible `dataset` artifact already supplied to `verify(...)`;
4. otherwise, a structured missing-source error.

The `dataset` fallback avoids requiring the same CSV path twice when one artifact supports both schema introspection and row lookup. It does not change the semantic distinction between these roles, and an explicit resolver or source always wins.

The runtime resolver MUST:

1. obtain the selected anchor source;
2. locate rows where `key == value`;
3. reject a missing match;
4. reject multiple matches;
5. project the model input features;
6. validate feature names and types;
7. construct one concrete immutable point;
8. preserve reference provenance for reports and replay.

The lookup key MAY be metadata that is not a model feature. When the same dataset is reused for introspection and lookup, extra metadata columns are excluded from the model schema whenever the model exposes an ordered named-input contract such as sklearn `feature_names_in_`.

Model introspection owns the expected feature schema. Anchor resolution owns row lookup. These responsibilities must not be conflated.

## Runtime-provided anchor values

The public API MAY supply concrete values for an anchor declared in the specification.

Conceptual example:

```python
verify(
    specification,
    model=model,
    anchors={"x0": row},
)
```

A runtime binding MUST match a declared anchor identifier unless a later API contract explicitly allows external-only declarations.

## Quantifier clauses

### Single binding

```forml
forall x0
```

```forml
exists candidate
```

### Multiple bindings

```forml
forall x0, x1
```

```forml
exists candidate, reference
```

A binder list is left-to-right syntactic sugar.

```forml
forall x0, x1
```

means:

```forml
forall x0
forall x1
```

### Ordered nesting

```forml
forall x0
exists x1
with domain(
    x0.age: [18, 90],
    x1.age: [18, 90]
)
where x1.age >= x0.age
=> target[x1] >= target[x0]
```

The binder order is semantically significant. Indentation is ignored by the parser and exists only for readability.

These layouts are equivalent:

```forml
forall x0
exists x1
=> P
```

```forml
forall x0
    exists x1
        => P
```

### Visibility

For:

```forml
forall x0
exists x1
=> P
```

`x0` and `x1` are visible in `P`. `x0` is visible while binding and restricting `x1`. An inner point is not visible outside its binder body.

### Shadowing

Shadowing is invalid in the V1 target language:

```forml
forall x0
exists x0
=> P
```

The compiler MUST reject the second `x0` declaration.

## Domains with several points

The canonical form uses one domain block after the binder chain:

```forml
forall x0, x1
with domain(
    x0.age: [18, 90],
    x0.income: [0, 200000],
    x1.age: [18, 90],
    x1.income: [0, 200000]
)
=> ...
```

Every domain subject MUST be explicitly qualified. Domain entries attach to the named point, not to a global default entity.

The initial profile keeps domain constraints unary. Relations between points belong in `where` or the assertion:

```forml
where x1.income >= x0.income
```

## Point-indexed model targets

### One model output, several evaluations

FORML V1 declares one scalar model output:

```forml
target := risk_score
```

The target name is not a collection and `target[x0]` does not select an output by index.

The brackets select the point of evaluation:

```forml
target[x0]
target[x1]
```

Example:

```forml
target[x1] - target[x0] <= max_delta
```

### Evaluation identity

Repeated occurrences of `target[x0]` refer to the same model evaluation. `target[x0]` and `target[x1]` refer to different evaluations.

Conceptually:

```text
evaluation(model, x0) != evaluation(model, x1)
```

while:

```text
evaluation(model, x0) == evaluation(model, x0)
```

## Short target references

The short form remains valid when one default point can be identified:

```forml
forall x0
=> target <= 0.8
```

Equivalent explicit form:

```forml
forall x0
=> target[x0] <= 0.8
```

With two visible eligible points, the short form is invalid:

```forml
forall x0, x1
=> target <= 0.8
```

The compiler MUST require either `target[x0]` or `target[x1]`.

## Short feature references

The same uniqueness rule applies to unqualified features.

Valid:

```forml
forall x0
=> age >= 18 -> target <= 0.8
```

Equivalent to:

```forml
forall x0
=> x0.age >= 18 -> target[x0] <= 0.8
```

Invalid:

```forml
forall x0, x1
=> age >= 18
```

The compiler MUST NOT choose one point silently.

Specification-constant lookup keeps its existing precedence over implicit feature lookup. Explicit `x0.age` always denotes a feature of `x0`.

## Direct assertion properties

A property may omit a scope prelude and `=>` when the assertion is self-contained through declared anchors or explicit point references.

```forml
anchor x0 := {
    age: 42,
    income: 55000
}

[BOUND]:
target[x0] <= 0.4 using Z3
```

With exactly one globally visible anchor, this short form may also be resolved:

```forml
[BOUND]:
target <= 0.4 using Z3
```

With several global anchors, implicit references are ambiguous unless the property selects one through `check_at`.

## `check_at` anchor selection

### Syntax

```forml
check_at <anchor_identifier>
=> <assertion>
```

Example:

```forml
anchor baseline := { ... }
anchor candidate := { ... }

[BOUND]:
check_at candidate
=> target <= 0.4
```

### Meaning

`check_at candidate`:

- MUST refer to an already declared concrete anchor;
- selects `candidate` as the default point for the property;
- does not declare a new point;
- does not perform dataset lookup by itself;
- does not introduce quantification.

The assertion is equivalent to:

```forml
target[candidate] <= 0.4
```

## `where` restrictions

### General syntax

```forml
<quantifier_chain>
[ with domain(...) ]
[ where <restriction> ]
=> <assertion>
```

Example:

```forml
forall x0, x1
where (
    x1.income >= x0.income
    and x1.age == x0.age
)
=> target[x1] <= target[x0]
```

### Universal meaning

```forml
forall x1
where R(x1)
=> P(x1)
```

means:

```text
forall x1: R(x1) -> P(x1)
```

### Existential meaning

```forml
exists x1
where R(x1)
=> P(x1)
```

means:

```text
exists x1: R(x1) and P(x1)
```

The user does not need to rewrite a restriction manually when changing quantifier polarity. The lowering layer owns this distinction.

For an ordered chain, the single `where` clause restricts the innermost binder while remaining allowed to reference every point visible at that position. Therefore:

```forml
forall x0
exists x1
where R(x0, x1)
=> P(x0, x1)
```

has the bounded meaning:

```text
forall x0: exists x1: R(x0, x1) and P(x0, x1)
```

while:

```forml
exists x0
forall x1
where R(x0, x1)
=> P(x0, x1)
```

has the bounded meaning:

```text
exists x0: forall x1: R(x0, x1) -> P(x0, x1)
```

These alternating forms remain capability-gated in the initial executable profile, but their language meaning is fixed.

## Natural neighborhood restrictions

### Canonical syntax

```forml
where x1 in neighborhood(
    of = x0,
    metric = Linf,
    eps = 0.05
)
```

The candidate precedes `in neighborhood`, while the anchor is named through `of`.

### Meaning

The restriction denotes a relation between two points:

```text
neighborhood(candidate=x1, anchor=x0, metric=Linf, eps=0.05)
```

The relation lowers to backend-compatible arithmetic constraints according to the metric and the model input schema.

### Requirements

- the candidate and anchor identifiers MUST be visible points;
- they MUST be distinct identifiers in the initial profile;
- `eps` MUST be a compatible non-negative numeric scalar;
- the metric MUST be supported by the selected backend profile;
- neighborhood expansion MUST preserve all constrained feature identities;
- the relation MUST not invent a point implicitly.

## `at` local verification sugar

### Canonical syntax

```forml
at <anchor> with <candidate> in neighborhood(
    metric = <metric>,
    eps = <scalar>
)
=> <assertion>
```

Example:

```forml
anchor x0 := {
    age: 42,
    income: 55000
}

[ROBUSTNESS]:
at x0 with x1 in neighborhood(
    metric = Linf,
    eps = 0.05
)
=> (target[x1] - target[x0] <= 0.02)
   and (target[x0] - target[x1] <= 0.02)
```

### Normative desugaring

The form above MUST lower to:

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

### Rules

- `x0` MUST already be a declared anchor;
- `x1` MUST be fresh in the property;
- `x1` is universally quantified;
- `of = x0` is implicit in the sugar;
- the assertion may use both points explicitly;
- short feature or target references are ambiguous because two points are visible, unless a later, explicitly documented default rule is introduced for this sugar.

The initial target contract therefore recommends explicit `target[x0]` and `target[x1]` inside `at` properties.

## Explicit adversarial search

`at` expresses a universal local guarantee. A search for an admissible violating point uses explicit existential syntax:

```forml
anchor x0 := { ... }

[ROBUSTNESS]:
exists x1
where x1 in neighborhood(
    of = x0,
    metric = Linf,
    eps = 0.05
)
=> (target[x1] - target[x0] > 0.02)
   or (target[x0] - target[x1] > 0.02)
```

A satisfiable result is a witness, not a counterexample to a source-level existential statement.

## Pairwise properties

A property is pairwise when its assertion or restrictions relate two points.

### Universal pairwise guarantee

```forml
[MONOTONICITY]:
forall x0, x1
with domain(
    x0.income: [0, 200000],
    x1.income: [0, 200000]
)
where (
    x1.income >= x0.income
    and x1.age == x0.age
    and x1.debt_ratio == x0.debt_ratio
)
=> target[x1] <= target[x0]
```

### Existential pair search

```forml
[LOGIC]:
exists x0, x1
with domain(
    x0.age: [18, 90],
    x1.age: [18, 90]
)
where x0.age != x1.age
=> target[x0] == target[x1]
```

Pairwise does not imply universal or existential quantification by itself. The source quantifier determines result interpretation.

The provisional `x ~ x'` syntax is not the target core form.

## Quantifier capability profile

### Required executable V1 forms

Homogeneous chains:

```forml
forall x0, x1
```

```forml
exists x0, x1
```

The backend may lower universal verification through existential refutation and existential properties through witness search.

### Representable but capability-gated forms

```forml
forall x0
exists x1
=> P(x0, x1)
```

```forml
exists x0
forall x1
=> P(x0, x1)
```

The parser, AST, semantic layer, and IR MUST preserve these sequences and their order. A backend that cannot execute them MUST issue a structured unsupported-capability diagnostic.

The compiler MUST NOT reinterpret alternating binders as independent free variables.

## Canonical complete examples

### Concrete point check

```forml
model := "credit_risk.joblib"
target := risk_score

anchor x0 := {
    age: 42,
    income: 55000,
    debt_ratio: 0.31
}

[BOUND]:
target[x0] <= 0.4 using Z3
```

### Referenced observation with `check_at`

```forml
model := "credit_risk.joblib"
target := risk_score

anchor applicant := ref(
    key = "customer_id",
    value = "C-1842"
)

[BOUND]:
check_at applicant
=> target <= 0.4 using Z3
```

### Global one-point guarantee

```forml
model := "credit_risk.joblib"
target := risk_score

[BOUND]:
forall x0
with domain(
    x0.age: [18, 90],
    x0.income: [0, 200000],
    x0.debt_ratio: [0, 1]
)
=> target <= 0.8 using Z3
```

### User-friendly local robustness

```forml
model := "credit_risk.joblib"
target := risk_score

anchor x0 := ref(
    key = "customer_id",
    value = "C-1842"
)

[ROBUSTNESS]:
at x0 with x1 in neighborhood(
    metric = Linf,
    eps = 0.05
)
=> (target[x1] - target[x0] <= 0.02)
   and (target[x0] - target[x1] <= 0.02) using Z3
```

### Explicit pairwise monotonicity

```forml
model := "credit_risk.joblib"
target := risk_score

[MONOTONICITY]:
forall x0, x1
with domain(
    x0.income: [0, 200000],
    x1.income: [0, 200000]
)
where x1.income >= x0.income
=> target[x1] <= target[x0] using Z3
```

## Invalid examples

### Undeclared anchor selection

```forml
[BOUND]:
check_at x0
=> target <= 0.4
```

Invalid because `x0` is not a declared anchor.

### Ambiguous target

```forml
forall x0, x1
=> target <= 0.4
```

Invalid because two points are eligible.

### Ambiguous feature

```forml
forall x0, x1
=> age >= 18
```

Invalid because the point owning `age` is not identified.

### Rebinding

```forml
forall x0
exists x0
=> target[x0] >= 0
```

Invalid because shadowing is forbidden.

### Anchor used as symbolic binder

```forml
anchor x0 := { age: 42 }

[LOGIC]:
forall x0
=> target[x0] >= 0
```

Invalid because `x0` is already bound globally as an anchor.

### Unknown target point

```forml
forall x0
=> target[x1] >= 0
```

Invalid because `x1` is not visible.

### Provisional pair syntax as target core

```forml
x ~ x'
=> ...
```

Not part of the normative target core. A migration layer may reject it or lower a supported legacy subset explicitly.

## Non-goals of this language slice

This specification does not add:

- multiple model outputs;
- multiple models in one property;
- general preprocessing reconstruction;
- partial anchors;
- named multiple anchor sources;
- relational domain declarations;
- unrestricted quantifier execution;
- remote data resolution;
- implicit point creation based on identifier spelling.

## Normative references

- ADR-0017 — First-Class Points, Lexical Bindings, and Point-Indexed Model Evaluations
- `contracts/point-binding-and-evaluation.md`
- `testing/point-binding-evaluation-test-matrix.md`

## Implementation closure

Patch 15.12 closed this specification for the numeric-affine V1 profile. Provisional legacy `at`, undeclared `check_at`, and `x ~ x'` forms are diagnostic-only. The explicit core and user-facing sugar now share one point-aware compiler, backend, reporting, and replay pipeline.
