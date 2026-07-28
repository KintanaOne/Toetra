# Specification constants

> Status: Implemented and semantically defined in `1.0.0rc3`
> Scope: Immutable scalar declarations in a `.toetra` header
> Audience: users and compiler contributors

## Purpose

Specification constants give business thresholds and reusable literals stable
names:

```toetra
model := "credit-risk.joblib"
target := risk

maximum_risk := 0.20
minimum_income := 25000.0

[LOGIC]:
forall applicant
with domain(
    applicant.income: [minimum_income, 200000.0]
)
=> target[applicant] <= maximum_risk using Z3
```

They are specification data, not model features, symbolic solver variables,
environment variables, or mutable program state.

## Declaration syntax

```text
identifier := scalar literal
```

Accepted literal families:

| Type | Examples |
|---|---|
| integer | `7`, `-3` |
| real | `0.20`, `-0.1` |
| Boolean | `true`, `false` |
| quoted string | `"EU"`, `"high risk"` |

Declarations appear after required `model` and `target` declarations and an
optional `dataset`, but before anchors and properties.

Canonical formatting uses one declaration per line. Optional semicolons are
accepted.

## Deliberate exclusions

The declaration right-hand side is one literal. These are not supported:

```text
annual_limit := monthly_limit * 12
regions := {"EU", "US"}
settings := { threshold: 0.2 }
```

Toetra has no constant dependency graph, local property constant, mutation, or
reassignment.

## Visibility and immutability

A specification constant:

- is visible to every property in the file;
- preserves its literal scalar type;
- cannot be redeclared;
- cannot collide with a point binder;
- cannot be assigned in a property body;
- is resolved before IR lowering while retaining source provenance.

## Assertion name resolution

In scalar-expression position:

```text
matching specification constant
→ implicit feature of the unique default point
→ unbound-name error
```

Example:

```toetra
maximum_risk := 0.20

[LOGIC]:
forall applicant
=> applicant.maximum_risk <= maximum_risk
```

The qualified left side is the feature `applicant.maximum_risk`; the bare right
side is the constant.

With no constant named `income`, this:

```toetra
income >= 25000
```

resolves to the implicit feature of the unique default point.

## Domain name resolution

Domain subjects are always explicit:

```toetra
applicant.income: [minimum_income, 200000.0]
```

Bare names in interval bounds may resolve to constants. They do not fall back to
implicit features. Write `applicant.margin` to reference a feature in a bound.

In finite-set member position:

```text
matching specification constant
→ symbolic categorical literal
```

```toetra
preferred_region := "EU"

[LOGIC]:
forall applicant
with domain(
    applicant.region: {preferred_region, US}
)
=> target[applicant] <= 1
```

`preferred_region` resolves to `"EU"`; `US` remains a symbolic literal.

## Typing

Each constant retains the type of its literal:

```text
7       → INT
0.20    → FLOAT
true    → BOOL
"EU"    → STRING
```

Semantic validation checks the use site. A declaration may be valid while one
use is not:

```text
maximum_score := "high"
target[point] <= maximum_score
```

For a numeric regression output, the comparison has incompatible types.

Numeric constants can participate in affine classification:

```toetra
coefficient := 2.0

[LOGIC]:
forall point
=> coefficient * point.income <= target[point]
```

The constant is compile-time numeric input to the scalar analysis, not an
unconstrained backend symbol.

## Backend boundary

Constants are language-level values. Public execution still depends on the use:

- numeric constants in affine expressions are supported by the numeric V1
  routes;
- string constants in categorical domains have accepted meaning but the
  built-in Z3 V1 profile cannot encode the categorical requirement;
- classification label literals must match the model output schema exactly.

## Failure ownership

| Failure | Boundary |
|---|---|
| non-literal declaration RHS | parser |
| duplicate declaration | semantic registration |
| constant/point-name collision | semantic registration |
| incompatible use-site type | semantic typing |
| valid categorical value without backend capability | route qualification |

## Related pages

- [Language support levels](support-levels.md)
- [Syntax](syntax.md)
- [Assertions](assertions.md)
- [Domains](domains.md)
- [Language examples](examples.md)
- [Specification constants contract](../contracts/specification-constants.md)
