# Syntax

> Status: Accepted syntax for `1.0.0rc3`
> Scope: User-facing `.toetra` source
> Audience: users, test authors, and language contributors

## Reading this page

This page answers “what parses and builds an AST?” It does not by itself promise
semantic validity or public execution. See
[Language support levels](support-levels.md) for those boundaries.

## Program structure

A file contains a header and at least one property:

```toetra
model := "linear.joblib"
target := score

[BOUND]:
forall applicant
=> target[applicant] <= 7 using Z3
```

Whitespace and newlines may separate grammar elements. Canonical examples use
one declaration per line and multiline scopes for readability.

Line comments begin with `#`. Triple-single-quoted blocks are ignored as block
comments.

## Header

Declarations appear in this order:

1. required `model`;
2. required `target`;
3. optional `dataset`;
4. zero or more specification constants;
5. zero or more anchors.

### Model, target, and dataset

```toetra
model := "model.joblib"
target := risk_score
dataset := "observations.csv"
```

`model` and `dataset` accept a quoted string or identifier. Canonical paths are
quoted. `target` accepts one identifier.

### Specification constants

```toetra
maximum_risk := 0.20
minimum_income := 25000
strict_mode := true
region := "EU"
```

The right-hand side is one signed number, Boolean, or quoted string literal.
Derived declarations do not parse:

```text
annual_limit := monthly_limit * 12
```

Semicolons between declarations are accepted, but one declaration per line is
the canonical style.

### Inline anchors

An inline anchor declares one concrete point:

```toetra
anchor customer := {
    age: 42,
    income: 58000.0
}
```

Feature names are unqualified inside the anchor. Values are signed numbers,
Booleans, or quoted strings. The block must not be empty.

### Referenced anchors

A referenced anchor selects one row from an external source:

```toetra
anchor customer := ref(
    key = "customer_id",
    value = "C-1842"
)
```

The grammar preserves the arguments. Semantic validation requires one usable
`key` and one usable `value`; the runtime resolves the row from the configured
anchor source or eligible dataset fallback.

## Properties

The general shape is:

```text
[PROPERTY]: [scope =>] assertion [using backend]
```

The recognized property labels are:

```text
ROBUSTNESS
STABILITY
FAIRNESS
MONOTONICITY
BOUND
LOGIC
```

The grammar also recognizes an unknown all-uppercase label so semantic
validation can issue a deliberate error. That parser behavior does not create
an extension mechanism.

### Scoped property

```toetra
[LOGIC]:
forall applicant
=> applicant.age >= 18 -> target[applicant] <= 0.20 using Z3
```

### Direct assertion property

A property may omit a scope when its point references are already available:

```toetra
anchor applicant := { age: 42, income: 58000.0 }

[BOUND]:
target[applicant] <= 0.20 using Z3
```

Semantic validation still requires every feature and model evaluation to have
an unambiguous point.

## Point scopes

### Quantified points

```toetra
[BOUND]:
forall applicant
=> target[applicant] <= 1
```

```toetra
[LOGIC]:
exists applicant
=> target[applicant] >= 0.8
```

Several same-kind points may share one clause:

```toetra
forall lower, higher
```

Ordered clauses also parse:

```toetra
forall baseline
exists candidate
```

The ordered chain is preserved. Alternation is outside the built-in V1 backend
capabilities even though it parses and has a structured representation.

Unicode `∀` and `∃` are accepted aliases for `forall` and `exists`.

### Domain attachment

A quantified scope may attach one domain:

```toetra
forall applicant
with domain(
    applicant.age: [18, 65]
)
=> target[applicant] <= 1
```

### Restrictions

One `where` restriction may follow a quantified scope:

```toetra
forall lower, higher
where higher.income >= lower.income
=> target[higher] >= target[lower]
```

A neighborhood restriction has an explicit candidate and anchor:

```toetra
forall candidate
where candidate in neighborhood(
    of = baseline,
    metric = Linf,
    eps = 0.1
)
=> target[candidate] <= target[baseline] + 0.02
```

The referenced anchor must already be visible.

### `check_at`

`check_at` selects a declared concrete anchor:

```toetra
anchor applicant := { age: 42, income: 58000.0 }

[BOUND]:
check_at applicant
=> target <= 1
```

An undeclared `check_at` name still parses so Toetra can produce a stable
migration diagnostic. It is not semantically valid.

### `at` local sugar

The current local form declares one symbolic candidate around an anchor:

```toetra
anchor baseline := { income: 50000.0 }

[ROBUSTNESS]:
at baseline with candidate in neighborhood(
    metric = Linf,
    eps = 0.1
)
=> target[candidate] - target[baseline] <= 0.02
```

It desugars to an explicit universal candidate with a neighborhood restriction.
Older `at name in neighborhood(...)` and pairwise `x ~ x'` forms are
diagnostic-only legacy syntax.

## Domains

Each domain entry has an explicitly qualified feature subject:

```toetra
with domain(
    applicant.age: [18, 65],
    applicant.debt_ratio: ]0.0, 1.0],
    applicant.score: [0.0, 1.0[,
    applicant.margin: ]0.0, 1.0[,
    applicant.segment_id: {1, 2, 3}
)
```

### Interval delimiters

| Form | Lower endpoint | Upper endpoint |
|---|---|---|
| `[a, b]` | closed | closed |
| `]a, b]` | open | closed |
| `[a, b[` | closed | open |
| `]a, b[` | open | open |

Parenthesis interval notation is not part of the language.

Bounds are scalar expressions:

```toetra
with domain(
    candidate.income: [baseline.income - 1000, baseline.income + 1000]
)
```

The grammar accepts this tree; semantic validation requires numeric bounds,
exact point bindings, and no `target` reference.

### Finite sets

```toetra
applicant.level: {1, 2, 3}
applicant.region: {EU, US}
applicant.channel: {"web", "branch"}
```

Unquoted identifiers in a finite set are symbolic literals. Their accepted
meaning does not imply that the built-in Z3 V1 route can encode categorical
features.

## Scalar expressions

Leaves are:

- numeric, Boolean, and string literals;
- specification constants and feature names;
- qualified features such as `applicant.income`;
- model evaluations and output observables;
- parenthesized scalar expressions.

Numeric arithmetic operators are:

```text
unary +  unary -
*  /
+  -
```

Examples:

```toetra
2 * applicant.income - applicant.debt
(target[applicant] - baseline_score) / 2
```

Arithmetic syntax is broader than the public affine execution profile.

## Comparisons and Boolean assertions

Comparison operators are:

```text
==  !=  <  <=  >  >=
```

Boolean operators are:

```text
not / NOT
and / AND
or  / OR
->
```

Example:

```toetra
(applicant.age >= 18 and target[applicant] <= 0.20)
or applicant.manual_review == true
```

Precedence from strongest to weakest is:

1. scalar parentheses;
2. unary arithmetic;
3. multiplication and division;
4. addition and subtraction;
5. comparison;
6. `not`;
7. `and`;
8. `or`;
9. `->`.

Implication is right-associative. Chained comparisons do not parse; write:

```toetra
0 <= applicant.score and applicant.score <= 1
```

## Model outputs

### Regression

```toetra
target[applicant] <= 0.20
```

When exactly one default point is eligible:

```toetra
target <= 0.20
```

### Binary classification

```toetra
target[applicant].label == "approved"
target[applicant].probability("approved") >= 0.80
```

The label argument is a signed number, Boolean, or quoted string literal.
Unknown observable names do not parse.

## Problem predicates

Problem/function syntax has this shape:

```toetra
CLASSIFICATION.EQUAL()
```

The grammar recognizes the vocabulary listed in [Vocabulary](vocabulary.md).
Only combinations named by the public profile are V1 executable.
`CLASSIFICATION.EQUAL()` is public sugar for predicted-label equality across
exactly two visible binary model evaluations.

## Backend syntax

```toetra
using Z3
using z3
```

An explicit backend is required, not a hint. Backend argument syntax is parsed,
but no DSL backend argument is part of the public V1 profile unless a backend
contract documents it.

ERAN, zonotope, and box spellings are reserved syntax and are rejected as V1
execution requests.

## Canonical formatting

- Quote artifact and dataset paths.
- Put declarations before properties.
- Use lowercase Boolean operators in new examples.
- Use explicit point indices in multi-point assertions.
- Use `Z3` consistently in public examples.
- Put each domain entry and neighborhood argument on its own line.
- Prefer explicit `forall`/`exists` and `where` forms in contracts; use `at` and
  `check_at` in user guides where their preconditions are clear.

## Related pages

- [Language support levels](support-levels.md)
- [Grammar](grammar.md)
- [Scopes](scopes.md)
- [Domains](domains.md)
- [Assertions](assertions.md)
- [Model output observables](model-output-observables.md)
- [Invalid examples](invalid-examples.md)
