# Properties

> Status: Accepted semantics for `1.0.0rc3`
> Scope: Property labels, scopes, and assertions
> Audience: users, semantic contributors, and backend authors

## Core rule

A property is a labelled verification request:

```text
property label
+ point context
+ assumptions and restrictions
+ assertion
+ optional required backend
```

The assertion and point context determine the logical formula. A label records
user intent and enables targeted validation; it does not inject hidden
mathematics.

## Structure

Scoped form:

```toetra
[BOUND]:
forall applicant
with domain(
    applicant.income: [0.0, 100000.0]
)
=> target[applicant] <= 1 using Z3
```

Direct form with a declared anchor:

```toetra
anchor applicant := { income: 50000.0 }

[BOUND]:
target[applicant] <= 1 using Z3
```

## Recognized labels

| Label | Intended use | Required explicit content |
|---|---|---|
| `ROBUSTNESS` | bounded change or neighborhood behavior | points, perturbation restriction, and stability assertion |
| `STABILITY` | output consistency under stated conditions | points/conditions and comparison assertion |
| `FAIRNESS` | relational behavior across points | at least two visible points and the intended relation |
| `MONOTONICITY` | ordered change between points | ordering restriction and output relation |
| `BOUND` | lower or upper output/property limit | point context and bound assertion |
| `LOGIC` | general typed logical rule | complete Boolean assertion |

All six labels are recognized by the language and may reach the Z3 route when
the model, points, domains, arithmetic, observables, and numeric policy satisfy
the public profile. The label alone does not make a route public.

## Scope ownership

A property may introduce symbolic points with `forall` or `exists`, select a
declared anchor with `check_at`, use local `at` sugar, or reference already
visible anchors directly.

Semantic validation establishes:

- the ordered point environment;
- one default point only when unambiguous;
- exact feature and target bindings;
- domain ownership;
- restriction visibility;
- one model evaluation identity per `(model, point, target)`.

Multi-point assertions should use explicit point qualification.

## Universal and existential meaning

For domain/model assumptions `Γ` and property assertion `P`:

```text
forall: search Γ ∧ ¬P for a counterexample
exists: search Γ ∧ P for a witness
```

This difference is preserved through IR2, reporting, and status interpretation.
Homogeneous universal or existential chains are public V1. Alternating chains
are represented but capability-rejected.

## Relational properties

### Monotonicity

```toetra
[MONOTONICITY]:
forall lower, higher
with domain(
    lower.income: [0.0, 100000.0],
    higher.income: [0.0, 100000.0]
)
where higher.income >= lower.income
=> target[higher] >= target[lower] using Z3
```

The label does not infer which feature is ordered or which direction is
monotone; the restriction and assertion state both.

### Fairness

`FAIRNESS` requires at least two visible points:

```toetra
[FAIRNESS]:
forall first, second
=> target[first] == target[second] using Z3
```

Whether this formula is a valid fairness claim for a concrete use case depends
on the domain and protected-attribute policy supplied by the author. Toetra
does not invent those assumptions.

### Robustness

```toetra
anchor baseline := { income: 50000.0 }

[ROBUSTNESS]:
forall candidate
where candidate in neighborhood(
    of = baseline,
    metric = Linf,
    eps = 0.1
)
=> target[candidate] - target[baseline] <= 0.02 using Z3
```

The neighborhood is an explicit assumption. The assertion states the behavior
that must remain stable.

## Problem predicates

Problem predicates are Boolean assertion leaves:

```toetra
CLASSIFICATION.EQUAL()
```

In public V1, this predicate is semantic sugar for predicted-label equality
across exactly two visible evaluations of a binary classification model. It
does not mean regression equality and is rejected without the required point
and output context.

Other problem/function words recognized by the grammar are not public execution
claims. See [Vocabulary](vocabulary.md).

## Property labels and backend selection

Every recognized property label is semantically compatible with Z3 in V1, but
route qualification still checks the complete IR2 requirements. A request may
therefore fail because of:

- an unsupported model or encoder;
- categorical or nonlinear requirements;
- quantifier alternation;
- an unsupported output observable;
- incompatible numeric policy;
- an explicitly requested unregistered backend.

That is a capability rejection, not an unknown property.

## Invalid property cases

- unknown or malformed property label;
- `FAIRNESS` with fewer than two visible points;
- ambiguous feature or target shorthand;
- assertion with a non-Boolean root;
- incompatible problem/function combination;
- invalid output observable for the model schema;
- explicit backend outside the V1 support set.

## Related pages

- [Language support levels](support-levels.md)
- [Scopes](scopes.md)
- [Assertions](assertions.md)
- [Model output observables](model-output-observables.md)
- [Backends syntax](backends.md)
- [Backend execution contract](../contracts/backend-execution-contract.md)
