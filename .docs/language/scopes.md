# Scopes

> Status: Implemented / stabilizing  
> Scope: Evaluation scopes and semantic contexts  
> Priority: P1  
> Audience: DSL users, semantic layer contributors, IR authors

## Purpose

Scopes define where a FORML property is evaluated.

They are the left-hand side of a property rule:

```forml
[PROPERTY]: scope => assertion
```

The scope is responsible for introducing variables, roles, default entity resolution, domains, and perturbation spaces.

In the compiler pipeline, scope syntax is transformed into a `SemanticContext`, then into `ScopeIR`.

---

## Scope Responsibilities

A scope defines:

| Responsibility | Example |
|---|---|
| Variables | `x`, `x'`, `_x` |
| Roles | anchor, perturbation, symbolic |
| Default entity | implicit `age` resolves to `x'.age` or `_x.age` |
| Neighborhood | `L2` ball with `eps=0.1` |
| Domain | `with age(18, 65)` |
| Semantic scope type | local, pointwise, pairwise, quantifier |

---

## `check_at` Scope

### Syntax

```forml
[BOUND]: check_at x => score >= 0
```

### Meaning

`check_at` evaluates a property at a single point.

Semantic context:

| Variable | Role |
|---|---|
| `x` | anchor |

Default entity:

```text
x
```

Implicit reference:

```forml
score >= 0
```

resolves to:

```text
x.score >= 0
```

### Typical Use Cases

- bounded outputs,
- local sanity checks,
- pointwise logical assertions,
- deterministic model checks.

---

## `at` Scope

### Syntax

```forml
[ROBUSTNESS]: at x in neighborhood(metric=L2, eps=0.1) => CLASSIFICATION.EQUAL()
```

### Meaning

`at` introduces an anchor point and an implicit perturbation around it.

Semantic context:

| Variable | Role |
|---|---|
| `x` | anchor |
| `x'` | perturbation |

Default entity:

```text
x'
```

This means:

```forml
age <= 30
```

is resolved as:

```text
x'.age <= 30
```

### Typical Use Cases

- robustness around a point,
- stability under perturbations,
- local counterexample search,
- neighborhood-constrained verification.

---

## Pairwise Scope

### Syntax

```forml
[FAIRNESS]: x ~ x' in neighborhood(metric=L2, eps=0.1) => CLASSIFICATION.EQUITY()
```

### Meaning

Pairwise scope compares two related points.

Semantic context:

| Variable | Role |
|---|---|
| `x` | anchor |
| `x'` | perturbation / paired point |

The semantic layer expects the right variable to be the primed version of the left variable.

Valid:

```text
x ~ x'
```

Invalid:

```text
x ~ y
```

unless the language later introduces explicit unrelated-pair semantics.

### Typical Use Cases

- fairness comparisons,
- monotonicity checks,
- counterfactual pairs,
- controlled feature perturbation.

---

## Quantifier Scope

### Syntax

```forml
[BOUND]: forall with age(18, 65) => score >= 0
```

or:

```forml
[BOUND]: exists with age(18, 65) => score < 0
```

### Meaning

A quantifier introduces an implicit symbolic variable.

Internal convention:

| Internal Variable | Role |
|---|---|
| `_x` | symbolic |

Default entity:

```text
_x
```

Implicit reference:

```forml
score >= 0
```

resolves to:

```text
_x.score >= 0
```

### Accepted User-Facing Forms

Potential accepted forms:

| User Form | Normalized Value |
|---|---|
| `forall` | `forall` |
| `∀` | `forall` |
| `exists` | `exists` |
| `∃` | `exists` |

---

## Neighborhoods

Neighborhoods define perturbation constraints.

Example:

```forml
in neighborhood(metric=L2, eps=0.1)
```

A neighborhood is attached to scopes such as `at` and pairwise.

Expected semantic representation:

```text
metric: L2
eps: 0.1
args: {...}
```

Neighborhoods later become part of:

- `SemanticContext`,
- `ScopeIR`,
- model-aware constraints,
- backend lowering.

---

## Domains

Domains restrict evaluation.

Example:

```forml
with age(18, 65)
```

A domain can represent:

- categorical values,
- numeric boundaries,
- subsets of input space,
- future symbolic constraints.

Current syntax is simple. Target semantics should define whether a domain represents enumeration, interval, or backend-specific constraint.

---

## Scope to SemanticContext

The semantic validator transforms scopes into `SemanticContext` objects.

| Scope Syntax | Semantic Scope | Variables | Default Entity |
|---|---|---|---|
| `check_at x` | pointwise | `{x: anchor}` | `x` |
| `at x` | local | `{x: anchor, x': perturbation}` | `x'` |
| `x ~ x'` | pairwise | `{x: anchor, x': perturbation}` | `x'` |
| `forall` | quantifier | `{_x: symbolic}` | `_x` |
| `exists` | quantifier | `{_x: symbolic}` | `_x` |

---

## Scope to IR

Scopes lower into `ScopeIR`.

`ScopeIR` should preserve:

- scope kind,
- variable roles,
- neighborhood constraints,
- domain constraints,
- enough information for assertion aggregation and backend lowering.

Example conceptual `ScopeIR`:

```text
kind: local
variables:
  x: anchor
  x': perturbation
neighborhood:
  metric: L2
  eps: 0.1
domain: null
```

---

## Testing Requirements

Each scope should be tested at:

| Layer | Requirement |
|---|---|
| Grammar | Valid and invalid syntax. |
| AST builder | Correct scope node. |
| Semantic validation | Correct context and default entity. |
| IR1 | Correct `ScopeIR`. |
| IR2 | Scope constraints preserved. |
| Miova | Mutated scopes fail or transform as expected. |
| Hypothesis | Generated scopes cover valid and invalid boundaries. |

---

## Related Documents

- [Properties](properties.md)
- [Assertions](assertions.md)
- [IR Scope](../ir/scope-ir.md)
- [AST to Semantic Contract](../contracts/ast-to-semantic.md)
