# FORML Syntax Specification

This document defines the **concrete syntax and semantics** of the FORML language.

FORML is a **declarative constraint language for machine learning models**.
It allows expressing *properties* over models in a formal, structured, and backend-agnostic way.

A key design principle of FORML is that **scope is implicit**, derived from syntax rather than explicitly declared.

---

## 1. Core Principle

In FORML, the **scope of a property is determined by its syntactic form**.

| Syntactic form | Induced scope | Semantics                                       |
| -------------- | ------------- | ----------------------------------------------- |
| `forall`       | Global        | Property must hold for all valid inputs         |
| `at x`         | Local region  | Property must hold in a neighborhood around `x` |
| `check_at x`   | Pointwise     | Property must hold for a specific input `x`     |
| `x ~ x'`       | Pairwise      | Property relates two inputs `x` and `x'`        |

There is **no explicit `scope` keyword**.

---

## 2. Property Declaration

A property is declared using the following structure:

```forml
[PROPERTY_TYPE]:
<property_expression> -> <assertion>
```

Example:

```forml
[ROBUSTNESS]:
x ~ x' in neighborhood(L2, eps=0.01) -> CLASSIFICATION.EQUAL()
```

---

## 3. Property Expressions

A property expression defines **where and how** the constraint applies.

### 3.1 Global (Quantified)

```forml
forall -> ...
```

**Semantics**:
The constraint must hold for all valid inputs.

---

### 3.2 Local (Neighborhood-based)

```forml
at x in neighborhood(L2, eps=0.01) -> ...
```

**Semantics**:
The constraint must hold for all inputs in a neighborhood around `x`.

---

### 3.3 Pointwise

```forml
check_at x -> ...
```

**Semantics**:
The constraint must hold for the specific input `x`.

---

### 3.4 Pairwise

```forml
x ~ x' in neighborhood(L2, eps=0.01) -> ...
```

**Semantics**:
The constraint relates two inputs `x` and `x'`, typically under a notion of proximity.

Typical interpretations include:

* robustness (small perturbations)
* fairness (counterfactual comparison)
* invariance constraints

The exact semantics may depend on the backend.

---

## 4. Neighborhoods

Neighborhoods define **how inputs are related or perturbed**.

General form:

```forml
<neighborhood>(<arg>=<value>, ...)
```

Example:

```forml
neighborhood(L2, eps=0.01)
```

Arguments are **named and typed**, enabling extensibility and backend compatibility.

---

## 5. Assertions

Assertions define **what must hold** once the scope is defined.

General form:

```forml
<PROBLEM_TYPE>.<FUNCTION>(...)
```

Example:

```forml
CLASSIFICATION.EQUAL()
```

---

## 6. Logical Constraints (Optional)

FORML also supports logical expressions:

```forml
(A -> B) AND NOT C
```

With operators:

* `AND`, `OR`
* `NOT`
* `->` (implication)

---

## 7. Variables and Symbols

Common symbols:

* `x`, `x'` : input instances
* `eps` : tolerance (ε)
* `norm` : distance type (e.g. `"L2"`)
* `output(x)` : model output

Variables are **symbolic**:

* no execution order
* no assignment semantics
* purely declarative

---

## 8. Design Philosophy

FORML is designed to be:

* **Declarative**: describe *what*, not *how*
* **Compositional**: syntax encodes semantics
* **Backend-agnostic**: compatible with multiple verification engines
* **Extensible**: arguments and functions can evolve without breaking syntax

---

## 9. Summary

A FORML property is composed of:

1. A **scope** (implicit via syntax)
2. A **relation** (e.g. pairwise, local)
3. A **constraint** (assertion)

Example:

```forml
[ROBUSTNESS]:
x ~ x' in neighborhood(L2, eps=0.01) -> CLASSIFICATION.EQUAL()
```

Which reads as:

> For any pair of inputs `x` and `x'` within an L2 neighborhood of radius 0.01,
> the model must produce the same classification output.

---
