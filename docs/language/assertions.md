# Assertions

> Status: Accepted syntax and semantics in `1.0.0rc3`
> Scope: Boolean property expressions
> Audience: users, semantic contributors, and backend authors

## Purpose

An assertion states what must hold in a property context:

```toetra
[LOGIC]:
forall applicant
=> applicant.age >= 18 -> target[applicant] <= 0.20
```

It is a Boolean tree built from comparisons, problem predicates, Boolean
operators, and parentheses.

## Atomic comparisons

```text
scalar expression
comparison operator
scalar expression
```

Examples:

```toetra
target[applicant] <= 0.20
applicant.age >= 18
applicant.segment == "A"
2 * applicant.income - applicant.debt >= 0
target[applicant].label != "rejected"
```

Comparison operators:

```text
==  !=  <  <=  >  >=
```

Ordering requires numeric operands. Equality and inequality require compatible
scalar types. Predicted labels support equality and inequality only.

## Name and point resolution

Explicit feature:

```toetra
applicant.age >= 18
```

Implicit feature with one default point:

```toetra
age >= 18
```

The second form resolves to `applicant.age` only when exactly one eligible
default point exists. Toetra never guesses in a multi-point context.

Model evaluation:

```toetra
target[applicant]
```

Short output reference:

```toetra
target
```

The short form is accepted only when one default point is unambiguous.

## Specification constants

In scalar-expression position, a bare name resolves in this order:

1. matching specification constant;
2. implicit feature of the unique default point;
3. unbound-name error.

```toetra
maximum_risk := 0.20

[LOGIC]:
forall applicant
=> applicant.maximum_risk <= maximum_risk
```

The qualified left side is a feature. The bare right side is the constant.

## Boolean composition

```toetra
applicant.age >= 18 and target[applicant] <= 0.20
not applicant.manual_review == true
applicant.segment == "A" or applicant.segment == "B"
applicant.age >= 18 -> target[applicant] <= 0.20
```

Lowercase and uppercase `and`, `or`, and `not` are accepted. New examples use
lowercase.

Precedence from strongest to weakest:

1. scalar parentheses and arithmetic;
2. comparison;
3. `not`;
4. `and`;
5. `or`;
6. implication `->`.

Implication is right-associative.

A numeric expression is not a predicate:

```text
applicant.income + applicant.savings and target <= 1
```

## Problem predicates

Problem predicates are Boolean leaves:

```toetra
CLASSIFICATION.EQUAL()
```

In public V1, `CLASSIFICATION.EQUAL()` is sugar for predicted-label equality
across exactly two visible binary model evaluations. Other recognized
problem/function spellings are not public execution promises.

## Regression and classification assertions

Regression:

```toetra
target[applicant] <= 0.20
target[candidate] - target[baseline] <= 0.02
```

Binary classification:

```toetra
target[applicant].label == "approved"
target[applicant].probability("approved") >= 0.80
target[first].label == target[second].label
```

The binary route excludes probability equality, probability arithmetic,
thresholds exactly `0` or `1`, and label ordering.

## Universal and existential interpretation

The assertion tree `P` is preserved while scope semantics determine the query:

```text
forall → Γdomain ∧ Γmodel ∧ ¬P
exists → Γdomain ∧ Γmodel ∧ P
```

A backend SAT result therefore means a counterexample for `forall` and a
witness for `exists`.

## Logical normalization

NNF treats each complete comparison or problem predicate as an atom. It moves
negations through Boolean structure without rewriting the inside of scalar
arithmetic.

For example:

```toetra
not (
    applicant.income <= 0
    or target[applicant] < 0
)
```

normalizes logically to the conjunction of the negated comparisons while
preserving their scalar trees and provenance.

## V1 execution boundary

The built-in V1 route supports assertions whose complete requirements fit:

- finite numeric model inputs;
- affine scalar arithmetic;
- supported regression or binary-classification observables;
- Boolean `not`, `and`, `or`, and implication;
- homogeneous quantified point contexts;
- Z3 capability and numeric qualification.

A valid assertion may still be capability-rejected when it contains nonlinear
arithmetic, categorical solver requirements, alternating quantifiers, or an
unsupported observable.

## Failure ownership

| Failure | Boundary |
|---|---|
| malformed expression or chained comparison | parser |
| ambiguous or unknown point/name | semantic binding |
| incompatible comparison/arithmetic types | semantic scalar typing |
| invalid problem/function context | semantic problem validation |
| unsupported expression requirements | route qualification |
| translation/execution failure after qualification | backend adapter |

## Related pages

- [Language support levels](support-levels.md)
- [Arithmetic expressions](arithmetic-expressions.md)
- [Model output observables](model-output-observables.md)
- [Properties](properties.md)
- [NNF](../compiler/lowering-minimization.md)
