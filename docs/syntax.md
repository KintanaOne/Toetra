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

## 6. Logical Constraints

FORML supports structured logical expressions inside assertions.

### 6.1 Grammar Overview

Assertions follow a standard logical structure with precedence:

- `NOT` (highest precedence)
- `AND`
- `OR`
- `->` (implication, right-associative)

General form:

```forml
A AND B -> C
```
Which is interpreted as:
```forml
(A AND B) -> C
```

### 6.2 Atomic Expressions

The smallest logical units are:

#### Attribute comparisons :
```forml
x.feature1 <= 0
```
General form:
```forml
<attribute> <operator> <value>
```
Where:

- <attribute> can be nested: x.feature.subfeature
- <operator> ∈ ==, !=, <, <=, >, >=
- <value> is a number, boolean, or string

#### Problem assertions
```forml
CLASSIFICATION.EQUAL()
```
These represent model-level constraints.

### 6.3 Composition

Logical expressions can be composed:
```forml
(x.feature1 <= 0 AND x.feature2 >= 1) -> CLASSIFICATION.EQUAL()
```
```forml
NOT (x.feature1 <= 0) OR CLASSIFICATION.EQUAL()
```
Parentheses can be used to control evaluation order.

### 6.4 Semantics
- Logical expressions define constraints over inputs and model outputs
- They are declarative, not executable
- They are later transformed into an internal logical representation (IR)

---

## 🆕 Section 7 — Variables and Attributes (FIXED)

## 7. Variables and Attributes

### 7.1 Variables

Variables represent **symbolic inputs** to the model.

Examples:

- `x`
- `x0`
- `x'` (used in pairwise relations)

They are:

- not assigned
- not evaluated directly
- used as symbolic references in constraints

---

### 7.2 Attributes

Attributes allow accessing features of an input:

```forml
x.feature1
x.feature1.subfeature
```
General form :
```forml
<identifier> { "." <identifier> }
```

### 7.3 Key Distinction
| Concept     | Meaning                 |
| ----------- | ----------------------- |
| `x`         | an input instance       |
| `x.feature` | a feature of that input |

### 7.4 Notes
- Variables are scoped implicitly via property expressions (at, check_at, x ~ x', etc.)
- There is no assignment or mutation
- All variables are purely symbolic
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
```forml
> For any pair of inputs `x` and `x'` within an L2 neighborhood of radius 0.01,
> the model must produce the same classification output.
```
---
