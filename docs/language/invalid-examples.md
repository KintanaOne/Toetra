# Invalid and unsupported examples

> Status: Current boundary taxonomy for `1.0.0rc3`
> Scope: Syntax errors, semantic errors, capability rejections, and outcomes
> Audience: users, test authors, and diagnostic maintainers

## Core distinction

```text
invalid syntax
≠ invalid semantics
≠ unsupported public route
≠ property not satisfied
```

This page freezes failure ownership, not final error wording. P26 may improve
messages without moving a failure to the wrong layer.

Invalid programs use `text` fences deliberately: they are documentation
fixtures for rejection, not executable examples.

## Syntax rejections

### Missing quantified identifier

```text
model := "linear.joblib"
target := score

[LOGIC]:
forall
=> target <= 7
```

Expected boundary: parser. `forall` and `exists` require an explicit identifier.

### Empty domain

```text
model := "linear.joblib"
target := score

[LOGIC]:
forall point
with domain()
=> target[point] <= 7
```

Expected boundary: parser. A domain contains at least one entry.

### Empty finite set

```text
model := "linear.joblib"
target := score

[LOGIC]:
forall point
with domain(
    point.level: {}
)
=> target[point] <= 7
```

Expected boundary: parser. A finite set contains at least one member.

### Parenthesis interval notation

```text
point.age: (18, 65]
```

Expected boundary: parser. Toetra uses `[a,b]`, `]a,b]`, `[a,b[`, or `]a,b[`.

### Derived specification constant

```text
model := "linear.joblib"
target := score

monthly_limit := 100
annual_limit := monthly_limit * 12

[LOGIC]:
forall point
=> target[point] <= annual_limit
```

Expected boundary: parser. Header constants accept scalar literals only.

### Unknown output observable

```text
target[point].logit >= 0
```

Expected boundary: parser. Internal model quantities are not DSL observables.

## Semantic rejections

These forms have recognizable structure but invalid meaning.

### Unknown explicit point

```text
model := "linear.joblib"
target := score

[BOUND]:
forall point
=> other.age >= 18
```

Expected boundary: semantic binding. Toetra must not alias `other` to `point`.

### Implicit domain subject

```text
model := "linear.joblib"
target := score

[LOGIC]:
forall point
with domain(
    age: [18, 65]
)
=> target[point] >= 0
```

Expected boundary: semantic domain validation. Domain subjects are explicitly
qualified; write `point.age`.

### Duplicate domain subject

```text
model := "linear.joblib"
target := score

[LOGIC]:
forall point
with domain(
    point.age: [18, 65],
    point.age: {21, 42}
)
=> target[point] >= 0
```

Expected boundary: semantic domain validation.

### Reversed or empty interval

```text
point.age: [65, 18]
point.age: ]18, 18[
```

Expected boundary: semantic domain validation when constant bounds make the
contradiction decidable.

### Target used in a domain

```text
with domain(
    point.age: [0, target]
)
```

Expected boundary: semantic domain validation. A domain restricts inputs, not
model outputs.

### Ambiguous shorthand

```text
model := "linear.joblib"
target := score

[LOGIC]:
forall first, second
=> target <= 1
```

Expected boundary: semantic binding. With two eligible points, write
`target[first]` or `target[second]`.

### Undeclared `check_at`

```text
model := "linear.joblib"
target := score

[BOUND]:
check_at point
=> target <= 1
```

Expected boundary: semantic migration validation. Declare `anchor point := ...`
before selecting it.

### Legacy local or pairwise scope

```text
[ROBUSTNESS]:
at point in neighborhood(L2, eps=0.1)
=> target <= 1
```

```text
[FAIRNESS]:
first ~ second in neighborhood(L2, eps=0.1)
=> target <= 1
```

Expected boundary: semantic migration validation. Use declared anchors,
explicit point binders, `where` restrictions, or current `at ... with ...`
sugar.

### Non-numeric arithmetic

```text
point.region + 1 <= target[point]
```

Expected boundary: semantic type validation when `region` is string or
categorical.

### Constant division by zero

```text
point.income / (1 - 1) <= target[point]
```

Expected boundary: semantic arithmetic validation.

### Duplicate constant or point collision

```text
maximum := 1
maximum := 2
```

```text
applicant := 7
[LOGIC]: forall applicant => target <= 1
```

Expected boundary: semantic constant registration.

### Classification output without observable

```text
model := "binary.joblib"
target := decision

[LOGIC]:
forall applicant
=> target[applicant] >= 0
```

Expected boundary: schema-aware semantic validation. A classification model
requires `.label` or `.probability(label)`.

### Invalid label operation

```text
target[applicant].label > "approved"
target[applicant].label + 1 == "approved"
```

Expected boundary: semantic output-observable typing. Labels support equality
and inequality, not ordering or arithmetic.

### Invalid `CLASSIFICATION.EQUAL()` context

```text
[ROBUSTNESS]:
forall applicant
=> CLASSIFICATION.EQUAL()
```

Expected boundary: semantic problem validation. The sugar requires exactly two
visible binary model evaluations.

### Reserved backend

```text
model := "linear.joblib"
target := score

[BOUND]:
forall point
=> target[point] <= 1 using ERAN
```

Expected boundary: semantic backend validation. ERAN is reserved syntax, not a
V1 backend.

## Valid language, unsupported built-in route

These requests may pass parsing and semantic validation. They fail capability
or profile qualification without approximation.

### Nonlinear multiplication

```toetra
model := "linear.joblib"
target := score

[LOGIC]:
forall point
=> point.a * point.b <= target[point] using Z3
```

Reason: nonlinear arithmetic exceeds the built-in affine profile.

### Symbolic denominator

```toetra
model := "linear.joblib"
target := score

[LOGIC]:
forall point
=> point.a / point.b <= target[point] using Z3
```

Reason: symbolic division exceeds the built-in affine profile.

### Categorical finite set

```toetra
model := "model.joblib"
target := score

[LOGIC]:
forall point
with domain(
    point.region: {EU, US}
)
=> target[point] <= 1 using Z3
```

Reason: the built-in V1 Z3 route has no public categorical sort/encoding.

### Alternating quantifiers

```toetra
model := "linear.joblib"
target := score

[LOGIC]:
forall baseline
exists candidate
=> target[candidate] >= target[baseline] using Z3
```

Reason: the ordered chain is represented, but the built-in V1 route supports
homogeneous chains only.

### Unsupported model profile

A syntactically and semantically valid property can still fail before routing
when the fitted artifact is a tree, ensemble, neural network, multiclass
classifier, sklearn `Pipeline`, calibrated wrapper, or other model excluded by
the public profile. That is model/profile rejection, not a language error.

## Verification outcomes are not compilation failures

After the request compiles and routes:

| Scope | Backend result | Public status |
|---|---|---|
| universal refutation | SAT | `COUNTEREXAMPLE` |
| universal refutation | UNSAT | `PROVED`, subject to numeric and vacuity policy |
| existential witness search | SAT | `WITNESS` |
| existential witness search | UNSAT | `NO_WITNESS`, subject to numeric policy |
| either | inconclusive execution | `UNKNOWN` |

An empty or inconsistent admissible domain can make a universal verification
vacuous. Reports preserve the vacuity diagnostic rather than treating it as a
parser, semantic, or backend capability failure.

## Related pages

- [Language support levels](support-levels.md)
- [Language examples](examples.md)
- [Domains](domains.md)
- [Arithmetic expressions](arithmetic-expressions.md)
- [Model output observables](model-output-observables.md)
- [Backend diagnostics](../backends/diagnostics.md)
