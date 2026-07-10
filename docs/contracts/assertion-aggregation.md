# Assertion Aggregation Contract

> Status: P0 / Accepted target contract  
> Scope: Property formula + domain/model assumptions → verification condition  
> Audience: IR2 builders, aggregation authors, runner authors and diagnostic authors

## Purpose

Aggregation builds the complete logical problem that a backend must solve.

A user property alone is not the complete verification condition.

---

## Inputs

Aggregation may receive:

- normalized user-property formula `P`;
- domain assumptions `Γdomain`;
- model assumptions `Γmodel`;
- neighborhood or future semantic assumptions;
- quantifier verification semantics;
- source/provenance metadata.

---

## Source Separation

Every assumption retains a source tag, at least:

```text
DOMAIN
MODEL
NEIGHBORHOOD
SEMANTIC
USER
```

Source separation is required before and after composition for diagnostics, traces and future unsat-core mapping.

---

## Universal Composition

For:

```forml
forall x0 with domain(...) => P
```

universal proof by refutation builds:

```text
Γdomain(x0)
AND Γmodel(x0, target)
AND NOT P(x0, target)
```

Expected interpretation:

| Solver outcome | FORML meaning |
|---|---|
| UNSAT | Universal property proved over the admissible domain. |
| SAT | Counterexample found. |
| UNKNOWN | Property not proved and no reliable counterexample conclusion. |

---

## Existential Composition

For:

```forml
exists x0 with domain(...) => P
```

witness search builds:

```text
Γdomain(x0)
AND Γmodel(x0, target)
AND P(x0, target)
```

Expected interpretation:

| Solver outcome | FORML meaning |
|---|---|
| SAT | Witness found; existential request satisfied. |
| UNSAT | No admissible witness exists. |
| UNKNOWN | Existence remains undecided. |

A runner/result model must use semantics-appropriate labels. `SAT` is not always a counterexample.

---

## Domain Composition

Within `Γdomain`:

- interval lower and upper restrictions are conjoined;
- finite-set members are disjoined;
- distinct domain entries are conjoined;
- arithmetic bound expressions remain scalar expressions;
- each generated component retains domain-entry provenance.

---

## Vacuity and Empty-Domain Diagnostics

An unsatisfiable `Γdomain ∧ Γmodel` can make a universal verification condition unsatisfiable independently of `P`.

Therefore the target aggregation/runtime contract should distinguish:

```text
property proved over a non-empty admissible set
```

from:

```text
verification condition unsatisfiable because the admissible set is empty
```

At minimum, FORML should be able to emit a vacuity warning when emptiness is detected. The exact strategy may be a pre-check, diagnostic query or unsat-core analysis.

For existential semantics, an empty admissible set directly means no witness exists.

---

## Provenance Invariant

The aggregated condition keeps a trace from every generated atom to:

- source property;
- source domain entry or model constraint;
- original scalar expression;
- normalization/negation step;
- final backend expression where possible.

Logical grouping may change, but provenance must not be discarded.

---

## Aggregation-Owned Failures

Aggregation rejects:

- missing quantifier verification semantics;
- missing required model assumptions;
- malformed assumption source tags;
- assumptions referring to entities absent from the scope;
- property/domain/model formulas whose scalar requirements conflict internally;
- a composition path that applies universal negation to existential semantics.

Backend support is checked later unless aggregation itself cannot represent the formula.
