# FORML Syntax Specification

This document defines the concrete syntax of the FORML language.

FORML is a **declarative constraint language** for machine learning models.
Its syntax encodes *where* a property applies **implicitly**, through
quantification and variable relationships.

There is no explicit `scope` keyword.

---

## 1. Core Principle

In FORML, **scope is a consequence of syntax**, not a declared attribute.

| Syntactic form       | Induced semantic scope | Semantic |
|----------------------|------------------------|----------|
| `forall x`           | Global                 | Property must be True for all instance |
| `at x`               | Local                  | For any instance in hyperballwith an anchor x, the property must be True |
| `check_at x`         | pointwise              | For an instance x, the property must be True |
| `x ~ x'`             | Pairwise               | For x and x' with distance d, the property must be True |

This makes FORML closer to logic and specification languages than to APIs.

---

## 2. Property Declaration

A property is defined by:

```forml
[PROPERTY_TYPE]:
...
```

## 3. Quantification Forms
### 3.1 Universal Quantification (Global)
```forml
[ROBUSTNESS]:
forall ...
```
**Semantique** :
The constraint must hold for all valid inputs.

### 3.2 Local Evaluation (Local region)
```forml
[ROBUSTNESS]:
at x ...
```
**Semantique** :
The constraint is evaluated at a specific region.

### 3.3 Pointwise Evaluation (Instance)
```forml
[ROBUSTNESS]:
check_at x ...
```
**Semantique** :
The constraint is evaluated at a specific input.

### 3.4 Pairwise Evaluation
```forml
[ROBUSTNESS]:
x ~ x' ...
```
**Semantique** :
The constraint is beetween two instances :
- similarity
- neighborhood
- same group
- counterfactual relation
- Its interpretation is backend-defined.

## 4. Constraint Expressions
### 4.1 Equality
```forml
output(x) == output(x')
```
### 4.2 Similarity / Tolerance
```forml
|output(x) - output(x')| <= ε
```
### 4.3 Order
```forml
output(x₁) <= output(x₂)
```
### 4.4 Bounds
```forml
a <= output(x) <= b
```
### 4.5 Logic
```forml
(A -> B) AND NOT C
```
## 5. Variables and Symbols

Common symbols:

- x, x' : inputs
- δ : perturbation
- ε : tolerance
- output(x) : model output

Variables are symbolic.
No execution order is implied.