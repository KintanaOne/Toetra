# FORML Semantic Model

This document defines the formal semantics of FORML.

While `syntax.md` specifies how properties are written,
this document defines **what they mean**, independently
of any parser, solver, or verification backend.

FORML specifications are interpreted as logical constraints
over a model viewed as a mathematical function.

---

## 1. The Model

A machine learning model is abstracted as a function:

    f : X → Y

Where:

- X is the input space
- Y is the output space
- f is deterministic

No assumptions are made about:

- architecture
- training process
- differentiability
- continuity

---

## 2. Variables and Inputs

Variables such as `x`, `x0`, `x'` denote elements of X.

They are:

- symbolic (not assigned)
- implicitly scoped by the property expression
- interpreted within a logical formula

A FORML specification does not execute the model.
It constrains its behavior.

---

## 3. Attribute Access

Attributes represent projections over input variables.

Example:

    x.feature1
    x.feature1.subfeature

Semantics:

An attribute is interpreted as a function:

    feature : X → V

So that:

    x.feature1  ≡  feature1(x)

Chained attributes are interpreted as function composition.

---

## 4. Neighborhoods and Relations

A neighborhood defines a relation over inputs.

Example:

    neighborhood(L2, eps=0.01)

Semantics:

A neighborhood induces a binary relation:

    R ⊆ X × X

Such that:

    (x, x') ∈ R  ⇔  d(x, x') ≤ ε

The exact definition of:

- distance d
- norm (L1, L2, Linf, etc.)
- admissible perturbations

is delegated to the backend.

---

## 5. Property Expressions (Scope Semantics)

In FORML, **scope is implicit and syntactically defined**.

---

### 5.1 Pointwise

```forml
check_at x -> P(x)
```
Semantics:
```forml
P(x₀)
```
for a specific input x₀ ∈ X.

### 5.2 Local (Neighborhood-based)
at x in neighborhood(...) -> P(x')

Semantics:

∀x' ∈ N(x₀), P(x')

where N(x₀) is the neighborhood of x₀.

### 5.3 Pairwise
```forml
x ~ x' in neighborhood(...) -> P(x, x')
```
#### Semantics:
```forml
∀(x, x') ∈ R, P(x, x')
```
where R is induced by the neighborhood.

### 5.4 Global (Quantified)
```forml
forall -> P(x)
```
#### Semantics:
```forml
∀x ∈ X, P(x)
```
## 6. Logical Semantics

Assertions are interpreted as logical formulas.

### 6.1 Atomic Expressions
#### Attribute comparisons
```forml
x.feature1 <= 0
```
##### Semantics:
```forml
feature1(x) ≤ 0
```
#### Problem-level predicates
```forml
CLASSIFICATION.EQUAL()
```
##### Semantics:

A predicate over the model output, e.g.:
```forml
f(x) = f(x')
```
depending on the context (pairwise, local, etc.)

### 6.2 Logical Operators

FORML supports standard propositional logic:

- AND (conjunction)
- OR (disjunction)
- NOT (negation)
- -> (implication)

Example:
```forml
A AND B -> C
```
#### Semantics:
```forml
(A ∧ B) ⇒ C
```
### 6.3 Structured Composition

Logical expressions form a tree:

- leaves: atomic predicates
- internal nodes: logical operators

Example:
```forml
(x.feature1 <= 0 AND x.feature2 >= 1) -> CLASSIFICATION.EQUAL()
```
#### Semantics:
```forml
(feature1(x) ≤ 0 ∧ feature2(x) ≥ 1) ⇒ EQUAL(f(x), ...)
```

## 7. Assertion Semantics

A FORML assertion defines a logical formula Φ.

A property:
```forml
[property]:
<property_expr> -> <assertion>
```
is interpreted as:
```forml
Scope(property_expr) ⇒ Φ(assertion)
```
Where:

- Scope(...) introduces quantification
- Φ(assertion) is the logical formula

## 8. Property Satisfaction

A property is satisfied if the induced formula is true under:

- input domain X
- relation R (if any)
- neighborhood definition
- interpretation of predicates

FORML does not decide satisfiability.

It defines the formula to be evaluated.

## 9. Backend Independence

FORML semantics is backend-agnostic.

Given a specification S, it defines a logical formula Φ(S).

A backend is responsible for:

- encoding Φ(S)
- solving or verifying it
- producing counterexamples if violated

## 10. Design Principles

FORML semantics is:

- declarative (no execution)
- compositional (tree-structured logic)
- extensional (defined on f)
- backend-independent

A FORML program denotes a logical constraint over a function f.


---