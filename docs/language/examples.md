# Language examples

> Status: Current examples for `1.0.0rc3`
> Scope: Accepted language with explicit support-level classification
> Audience: users, compiler authors, and test authors

## How to read the examples

Every complete source example is classified as one of:

- **public V1 route shape**: executable when the supplied artifact and runtime
  inputs satisfy the exact public profile;
- **accepted language**: parses and has defined semantics, but the built-in V1
  route cannot execute one or more requirements;
- **syntax-only illustration**: shows a grammar form whose semantic
  preconditions depend on an external model schema or runtime source.

Parsing a filename such as `linear.joblib` does not prove that the file exists,
is fitted, or has the required model family. See
[Language support levels](support-levels.md).

## V1-REG-001 — Universal regression bound

Classification: **public V1 regression route shape**

```toetra
model := "linear.joblib"
target := score

maximum_score := 7.0
minimum_income := 0.0
maximum_income := 100000.0

[BOUND]:
forall applicant
with domain(
    applicant.income: [minimum_income, maximum_income]
)
=> target[applicant] <= maximum_score using Z3
```

Meaning:

```text
For every admissible applicant,
search domain assumptions ∧ model equation ∧ ¬(score <= maximum_score).
```

The route is public when `linear.joblib` is a fitted, single-output,
finite-numeric scikit-learn `LinearRegression` whose feature schema contains
`income`.

## V1-REG-002 — Existential witness

Classification: **public V1 regression route shape**

```toetra
model := "linear.joblib"
target := score

[LOGIC]:
exists applicant
with domain(
    applicant.income: [0.0, 100000.0]
)
=> target[applicant] >= 0.8 using Z3
```

The verification condition searches:

```text
domain assumptions ∧ model equation ∧ (score >= 0.8)
```

SAT produces `WITNESS`; UNSAT produces `NO_WITNESS`; an inconclusive backend
attempt produces `UNKNOWN`.

## V1-REG-003 — Concrete inline anchor

Classification: **public V1 regression route shape**

```toetra
model := "linear.joblib"
target := score

anchor applicant := {
    income: 58000.0
}

[BOUND]:
check_at applicant
=> target <= 1.0 using Z3
```

`check_at` selects a declared anchor. It is not a quantifier and does not create
a symbolic domain.

## V1-REG-004 — Referenced anchor

Classification: **public V1 regression route shape with runtime input**

```toetra
model := "linear.joblib"
target := score

anchor applicant := ref(
    key = "customer_id",
    value = "C-1842"
)

[BOUND]:
check_at applicant
=> target <= 1.0 using Z3
```

The language preserves the lookup. Execution also requires a compatible anchor
source or eligible dataset fallback containing exactly one matching row and all
model features.

## V1-REG-005 — Local robustness sugar

Classification: **public V1 regression route shape**

```toetra
model := "linear.joblib"
target := score

anchor baseline := {
    income: 50000.0
}

[ROBUSTNESS]:
at baseline with candidate in neighborhood(
    metric = Linf,
    eps = 1000.0
)
=> (target[candidate] - target[baseline] <= 0.02)
   and (target[baseline] - target[candidate] <= 0.02) using Z3
```

The `at` form introduces a universally quantified candidate and a neighborhood
restriction around `baseline`. The explicit output indices make the two model
evaluations unambiguous.

## V1-REG-006 — Two-point monotonicity

Classification: **public V1 regression route shape**

```toetra
model := "linear.joblib"
target := score

[MONOTONICITY]:
forall lower, higher
with domain(
    lower.income: [0.0, 100000.0],
    higher.income: [0.0, 100000.0]
)
where higher.income >= lower.income
=> target[higher] >= target[lower] using Z3
```

The property label records monotonicity intent. The `where` restriction states
the input order; the assertion states the required output order.

## V1-CLS-001 — Binary class probability

Classification: **public V1 binary-classification route shape**

```toetra
--8<-- "docs/snippets/binary-probability.toetra"
```

The route additionally requires a direct fitted binary scikit-learn
`LogisticRegression`, two supported labels, finite numeric learned state, and
the numeric qualification rules in the public profile.

## V1-CLS-002 — Predicted-label relation

Classification: **public V1 binary-classification route shape**

```toetra
model := "binary.joblib"
target := decision

[FAIRNESS]:
forall first, second
=> target[first].label == target[second].label using Z3
```

The label equality is declarative. Toetra lowers it through the recognized
binary decision semantics without exposing a logit or framework class index.

## V1-CLS-003 — Classification equality sugar

Classification: **public V1 binary-classification route shape**

```toetra
model := "binary.joblib"
target := decision

[ROBUSTNESS]:
forall baseline, candidate
=> CLASSIFICATION.EQUAL() using Z3
```

`CLASSIFICATION.EQUAL()` requires exactly two visible model-input points and is
equivalent to predicted-label equality for the supported binary profile.

## LANG-DOM-001 — Boundary preservation

Classification: **accepted syntax and semantics**

```toetra
model := "linear.joblib"
target := score

[LOGIC]:
forall point
with domain(
    point.closed: [0, 3],
    point.open_left: ]0, 3],
    point.open_right: [0, 3[,
    point.open: ]0, 3[
)
=> target[point] >= 0
```

The four domain entries preserve, respectively:

| Source | Lower relation | Upper relation |
|---|---|---|
| `[0, 3]` | `>=` | `<=` |
| `]0, 3]` | `>` | `<=` |
| `[0, 3[` | `>=` | `<` |
| `]0, 3[` | `>` | `<` |

Execution additionally requires the model schema to expose all four finite
numeric features.

## LANG-ARI-001 — Affine precedence

Classification: **accepted language; V1-executable when the route qualifies**

```toetra
model := "linear.joblib"
target := score

[LOGIC]:
forall account
=> account.revenue - 2 * account.cost + account.reserve
   <= target[account] + 7 using Z3
```

Multiplication binds before addition and subtraction. Additive operations are
left-associative. The full comparison remains one logical atom during NNF.

## LANG-NONLINEAR-001 — Valid language, unsupported arithmetic

Classification: **accepted language; capability-rejected by built-in V1**

```toetra
model := "linear.joblib"
target := score

[LOGIC]:
forall point
=> point.a * point.b <= target[point] using Z3
```

For numeric features, semantic analysis classifies the product as nonlinear.
The built-in affine Z3 route rejects the requirement; it does not linearize or
approximate it.

## LANG-CAT-001 — Valid categorical domain, unsupported backend sort

Classification: **accepted language; capability-rejected by built-in V1**

```toetra
model := "model.joblib"
target := score

preferred_region := "EU"

[LOGIC]:
forall applicant
with domain(
    applicant.region: {preferred_region, US}
)
=> target[applicant] <= 1 using Z3
```

`preferred_region` resolves to a string specification constant and `US` remains
a symbolic categorical literal. When the model schema confirms categorical
meaning, the request is semantically valid. The built-in V1 Z3 profile has no
public categorical encoding and must reject it during route qualification.

## LANG-QUANT-001 — Represented quantifier alternation

Classification: **accepted language; capability-rejected by built-in V1**

```toetra
model := "linear.joblib"
target := score

[LOGIC]:
forall baseline
exists candidate
with domain(
    baseline.income: [0.0, 100000.0],
    candidate.income: [0.0, 100000.0]
)
=> target[candidate] >= target[baseline] using Z3
```

The ordered quantifier chain is preserved through the language pipeline.
Alternation exceeds the built-in V1 backend capability and is not flattened
into a homogeneous query.

## Example maintenance rule

Each example must retain:

- its support-level classification;
- complete source when fenced as `toetra`;
- explicit point qualification in multi-point assertions;
- a route caveat whenever execution depends on model/runtime inputs;
- no backend or model claim broader than the public profile.

Selected canonical examples are parsed or compiled by `make snippets-check`.
Release demos and parser, semantic, and end-to-end tests remain the executable
evidence for the wider example set.

## Related pages

- [Language support levels](support-levels.md)
- [Public V1 profile](../public-v1-profile.md)
- [Scopes](scopes.md)
- [Domains](domains.md)
- [Arithmetic expressions](arithmetic-expressions.md)
- [Model output observables](model-output-observables.md)
- [Invalid and unsupported examples](invalid-examples.md)
