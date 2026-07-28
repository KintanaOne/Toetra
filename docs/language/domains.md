# Domains

> Status: Accepted syntax and semantics in `1.0.0rc3`
> Scope: Typed input assumptions attached to quantified points
> Audience: users, semantic contributors, and backend authors

## Purpose

A domain restricts admissible model inputs:

```toetra
[BOUND]:
forall applicant
with domain(
    applicant.age: [18, 65],
    applicant.segment_id: {1, 2, 3}
)
=> target[applicant] <= 1
```

Domain entries are assumptions over input features. They are not assertions
about `target`.

## Placement and ownership

One domain may follow a quantified point chain and precede an optional `where`
restriction:

```text
quantifier clauses
→ domain
→ where restriction
→ =>
→ assertion
```

Every domain subject is explicitly qualified:

```toetra
applicant.age: [18, 65]
```

Semantic validation requires:

- the point to be visible in the enclosing scope;
- the feature to exist when a model schema is available;
- no duplicate `(point, feature)` subject;
- one interval or finite-set constraint per entry.

This is invalid even when one default point exists:

```text
age: [18, 65]
```

Implicit feature resolution is available in assertions, not domain subjects.

## Numeric intervals

Toetra uses square-bracket glyphs for all four endpoint combinations:

| Source | Lower | Upper |
|---|---|---|
| `[a, b]` | closed | closed |
| `]a, b]` | open | closed |
| `[a, b[` | closed | open |
| `]a, b[` | open | open |

Examples:

```toetra
applicant.closed: [0.0, 1.0]
applicant.open_lower: ]0.0, 1.0]
applicant.open_upper: [0.0, 1.0[
applicant.open: ]0.0, 1.0[
```

Parenthesis interval notation is not accepted.

### Bound validation

Interval bounds are scalar expressions:

```toetra
candidate.income: [
    baseline.income - tolerance,
    baseline.income + tolerance
]
```

Validation requires:

- numeric bound types;
- exact binding for every feature reference;
- no model-output reference;
- no constant division by zero;
- non-reversed constant bounds;
- both endpoints closed when equal constant bounds describe a singleton.

Domain entries have simultaneous logical meaning. A later entry is not an
assignment that can depend on a value produced by an earlier entry.

## Finite sets

```toetra
applicant.level: {0, 1, 2}
applicant.region: {EU, US}
applicant.channel: {"web", "branch"}
```

A finite set contains at least one member. Members may be scalar literals,
specification constants, or symbolic categorical literals.

In finite-set value position, a bare identifier resolves as:

1. a matching specification constant;
2. otherwise a symbolic categorical literal.

For example:

```toetra
preferred_region := "EU"

[LOGIC]:
forall applicant
with domain(
    applicant.region: {preferred_region, US}
)
=> target[applicant] <= 1
```

`preferred_region` is the string constant `"EU"`; `US` is a symbolic literal.
Semantic validation checks member compatibility when the feature schema is
known.

## Specification constants in bounds

Bare names in interval bounds may resolve to specification constants:

```toetra
minimum_income := 25000.0
maximum_income := 200000.0

[LOGIC]:
forall applicant
with domain(
    applicant.income: [minimum_income, maximum_income]
)
=> target[applicant] <= 1
```

Feature references inside bounds remain explicit. Without a constant named
`margin`, this is invalid:

```text
applicant.income: [margin - 1, margin + 1]
```

Write `applicant.margin` when referring to a feature.

## Logical meaning

Each interval becomes a conjunction of endpoint relations:

```text
point.age: ]18, 65]
→ point.age > 18 ∧ point.age <= 65
```

Each finite set becomes a disjunction of equalities:

```text
point.level: {1, 2, 3}
→ point.level == 1 ∨ point.level == 2 ∨ point.level == 3
```

Entries in one domain are conjoined.

For a universal property, domain assumptions participate in counterexample
search:

```text
Γdomain ∧ Γmodel ∧ ¬P
```

For an existential property, they participate in witness search:

```text
Γdomain ∧ Γmodel ∧ P
```

## Representation boundary

The current compiler preserves domains as:

```text
DomainNode
→ DomainIR with IntervalDomainIR / FiniteSetDomainIR
→ provenanced AssumptionIR2 values
```

Open/closed endpoint kinds and source ownership survive until assumption
encoding. The language and IR remain backend-independent.

## V1 execution boundary

The public numeric-affine routes support:

- finite numeric features;
- numeric interval bounds in the affine scalar profile;
- numeric finite sets encodable by Z3;
- homogeneous point quantifiers;
- domain provenance in reports.

Accepted language outside the built-in V1 route includes symbolic/string
categorical membership and any bound expression whose requirements exceed the
affine capability profile. Those requests are rejected during qualification,
not approximated.

## Failure ownership

| Failure | Boundary |
|---|---|
| empty domain/set or malformed delimiters | parser |
| implicit or unknown subject | semantic binding |
| duplicate subject | semantic domain validation |
| incompatible bound/member type | schema-aware semantic validation |
| reversed or empty constant interval | semantic domain validation |
| `target` in a subject or bound | semantic domain validation |
| categorical or unsupported arithmetic requirement | route qualification |

## Related pages

- [Language support levels](support-levels.md)
- [Syntax](syntax.md)
- [Scopes](scopes.md)
- [Arithmetic expressions](arithmetic-expressions.md)
- [Specification constants](specification-constants.md)
- [Typed domain IR1](../compiler/ir1-layer.md)
- [Quantified domain contract](../contracts/quantified-domain-scalar-expressions.md)
