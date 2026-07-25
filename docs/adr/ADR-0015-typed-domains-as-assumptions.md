# ADR-0015 — Preserve Typed Domains and Lower Them into Provenanced Assumptions

> Status: Accepted  
> Date: 2026-07  
> Scope: DSL domains, semantic validation, IR, assertion aggregation, and verification semantics

## Context

A FORML domain restricts the admissible valuations of input variables introduced by a property scope.

The earlier domain representation is effectively opaque:

```text
Domain(name, raw_values)
```

This shape cannot preserve the difference between:

- open and closed interval boundaries;
- numeric intervals and finite discrete sets;
- numeric, boolean, string, and symbolic categorical values;
- constant and arithmetic interval bounds;
- the domain subject and the values used to constrain it;
- source provenance required for diagnostics and counterexamples.

A domain is also not merely parser metadata. It contributes logical assumptions to the final verification problem and must therefore cross compiler boundaries in a typed, inspectable form.

## Decision

FORML represents domains as typed structured constraints and lowers them into explicit assumptions with domain provenance before backend execution.

### Surface syntax

A domain block contains one or more entries:

```toetra
with domain(
    x0.a: [0.0, 3.0],
    x0.b: {obj1, obj2},
    x0.c: ]0.0, 3.0],
    x0.d: {0.0, 7.0},
    x0.e: ]0.0, 3.0[
)
```

Every entry has the conceptual form:

```text
qualified_attribute : domain_constraint
```

The initial domain constraints are:

- numeric intervals;
- finite discrete sets.

Curly braces always denote a finite set, including for numeric members. They never denote an interval.

### Explicit subject binding

Domain subjects are always explicitly qualified.

For:

```toetra
forall x0
```

this is valid:

```toetra
x0.age: [18, 65]
```

while these are invalid:

```toetra
age: [18, 65]
y.age: [18, 65]
```

The subject entity must resolve exactly to a variable declared by the enclosing scope. `target` is prohibited as a domain subject.

### Typed interval representation

Intervals preserve:

- lower bound expression;
- upper bound expression;
- lower boundary kind;
- upper boundary kind.

Boundary kinds use an enum-like representation:

```text
EnumBoundaryKind.OPEN
EnumBoundaryKind.CLOSED
```

They are not represented by positional booleans.

The four supported notations are:

```text
[a, b]
]a, b]
[a, b[
]a, b[
```

### Typed finite-set representation

Finite-set members preserve their scalar type and source meaning.

Examples:

```toetra
x0.active: {true, false}
x0.code: {1, 7}
x0.region: {EU, US}
x0.label: {"A", "B"}
```

Unquoted identifiers in finite sets are symbolic categorical literals, not variable references. Their semantic compatibility is checked against the subject feature type or schema.

### Arithmetic interval bounds

Numeric interval bounds may be scalar arithmetic expressions:

```toetra
with domain(
    x0.a: [x0.b - 1.0, x0.b + 1.0]
)
```

All feature references inside domain bounds are explicitly qualified and must resolve to variables declared by the enclosing scope. `target` is prohibited in domain bounds because a domain defines admissible model inputs, not output-dependent preconditions.

Domain entries have simultaneous logical semantics. They are not sequential assignments evaluated in source order.

### Compiler representation and lowering

The parser, AST, semantic layer, and IR1 preserve a typed domain representation. The domain must not be reduced to an untyped name-and-arguments container.

Before the final verification condition is built, typed domain constraints are lowered into explicit backend-independent assumptions carrying:

```text
AssumptionSource.DOMAIN
```

Conceptual lowering examples follow.

Closed interval:

```toetra
x0.a: [0, 3]
```

becomes:

```text
x0.a >= 0
AND
x0.a <= 3
```

Open interval:

```toetra
x0.a: ]0, 3[
```

becomes:

```text
x0.a > 0
AND
x0.a < 3
```

Finite set:

```toetra
x0.region: {EU, US}
```

becomes:

```text
x0.region == EU
OR
x0.region == US
```

Multiple domain entries are conjoined.

Every generated assumption must remain traceable to its original domain entry and boundaries or set members.

### Verification semantics

For a universal property under refutation semantics, the verification condition is conceptually:

```text
Γdomain(x)
AND
Γmodel(x, target)
AND
NOT P(x, target)
```

Unsatisfiability proves that no admissible input violates the property.

For an existential property, the witness-search condition is conceptually:

```text
Γdomain(x)
AND
Γmodel(x, target)
AND
P(x, target)
```

The universal refutation condition must not be reused unchanged for existential semantics.

### Domain validity and vacuity

The semantic layer rejects statically detectable malformed domains, including:

- empty domain blocks;
- duplicate subjects;
- empty finite sets;
- incompatible set member types;
- reversed constant intervals;
- constant intervals that are empty because of open boundaries;
- non-numeric interval bounds;
- unresolved entities;
- target references in subjects or bounds;
- literal division by zero in arithmetic bounds.

A symbolic domain may still be unsatisfiable even when no local semantic rule can prove it. FORML should expose domain-satisfiability or vacuity diagnostics when the verification pipeline can determine that the admissible set is empty.

## Rationale

Typed domains preserve user intent across every compiler boundary and allow the domain to participate in verification without backend leakage.

Lowering them into explicit assumptions provides a uniform final composition model:

```text
user property
+ domain assumptions
+ model assumptions
+ future neighborhood or semantic assumptions
```

Provenance is essential because a counterexample, an unsatisfiable core, or a vacuity warning should be explainable in terms of the original domain entry rather than anonymous solver clauses.

## Consequences

### Positive

- Open and closed boundaries remain explicit.
- Finite sets are not confused with numeric intervals.
- Domain typing can use ModelSchema information.
- Domain constraints are inspectable before backend lowering.
- IR2 aggregation can compose domain and model assumptions uniformly.
- Diagnostics and counterexamples can reference source domain entries.
- Universal and existential semantics can be built soundly.
- Backend routing can reason about interval, finite-set, categorical, and arithmetic requirements.

### Negative

- Domain AST and IR types become more numerous.
- Semantic validation must recurse through bound expressions and set members.
- Categorical finite sets require typed backend symbols or enum/string encodings.
- Provenance metadata must survive expansion into multiple assumptions.
- Symbolically unsatisfiable domains require additional diagnostics to avoid misleading vacuous proofs.
- Existing opaque `DomainIR(name, args)` consumers must migrate.

## Alternatives considered

### Keep `Domain(name, raw_values)`

Rejected because it cannot represent boundary kinds, typed members, subjects, arithmetic bounds, or reliable provenance.

### Desugar domains directly into the assertion during parsing

Rejected because parsing should preserve syntax rather than perform semantic logical expansion. It would also erase the distinction between assumptions and the property being verified.

### Lower domains directly to Z3

Rejected because domains are backend-independent semantic constraints and must participate in requirements analysis, aggregation, diagnostics, and alternative backend routing.

### Represent open or closed bounds with booleans

Rejected because enum-like boundary kinds are self-describing and less error-prone than positional boolean flags.

### Treat every unquoted finite-set identifier as a variable reference

Rejected because domain sets need concise categorical literals such as `{EU, US}`. Variable references belong to arithmetic interval expressions and are explicitly qualified.

### Allow arbitrary boolean predicates inside `domain(...)` immediately

Deferred. The initial structured entry form provides common interval and membership constraints with clearer typing and diagnostics. Arbitrary relational domain predicates may be introduced later as a separate language decision.

## Impact on FORML

### Grammar

`domain` becomes a protected keyword. The grammar distinguishes domain entries, interval forms, finite sets, boundary tokens, scalar values, and arithmetic interval bounds.

### AST

The domain becomes a collection of typed constraints. Interval and finite-set nodes preserve subjects, values, boundary kinds, and source locations.

### Semantic validation

The validator checks exact scope binding, feature types, interval validity, set compatibility, duplicate subjects, target prohibition, and recursive arithmetic references.

### IR1

`ScopeIR.domain` stores a typed backend-independent domain rather than opaque arguments.

### IR2 and aggregation

A dedicated lowering step expands each typed constraint into one or more assumptions tagged with `AssumptionSource.DOMAIN`. Assumption provenance is preserved through normalization and verification-condition construction.

### Backend requirements

Requirements analysis must distinguish at least:

- numeric interval comparisons;
- open and closed bounds;
- finite-set membership;
- categorical or string symbols;
- arithmetic interval bounds;
- domain assumptions.

### Tests

Required tests include:

- all four interval boundary combinations;
- exact quantified-subject binding;
- implicit domain subject rejection;
- mismatched entity rejection;
- numeric, boolean, string, and symbolic categorical sets;
- numeric set versus interval distinction;
- empty and duplicate entry rejection;
- constant empty and reversed interval rejection;
- arithmetic bound binding and typing;
- target prohibition;
- simultaneous-domain semantics;
- lowering to correctly tagged assumptions;
- provenance preservation;
- universal refutation composition;
- existential witness composition;
- vacuity diagnostics for detectable empty domains.

### Related documentation

- `language/domains.md`
- `language/quantified-bindings.md`
- `language/arithmetic-expressions.md`
- `contracts/ast-to-semantic.md`
- `contracts/semantic-to-ir1.md`
- `contracts/assertion-aggregation.md`
- `ir/aggregated-assertion-set.md`
- `backends/capabilities.md`
- `backends/z3.md`
