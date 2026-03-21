 cc<    # FORML Semantic Model

This document defines the formal semantics of FORML.

While `syntax.md` specifies how properties are written,
this document defines **what they mean** independently
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

## 2. Inputs and Variables

Variables such as `x`, `x'` are elements of X.

They are symbolic unless explicitly instantiated.

A specification never executes the model.
It constrains its behavior.

---

## 3. Perturbations

A perturbation δ is an element of X such that:

    x + δ ∈ X

The interpretation of `+` depends on the input structure.
FORML does not prescribe a metric or norm.

Backends may interpret perturbations using:
- Lp norms
- discrete flips
- structured transformations

---

## 4. Quantification Semantics

### 4.1 Universal Quantification

`forall x : P(x)`

Semantics:

    ∀x ∈ X, P(x) holds.

---

### 4.2 Local Evaluation

`at x : P(x)`

Semantics:

The property is evaluated at a specific input x₀ ∈ X.

This does not imply universal validity.

---

### 4.3 Relational Quantification

`forall x ~ x' : P(x, x')`

Let R ⊆ X × X be a binary relation.

Semantics:

    ∀(x, x') ∈ R, P(x, x') holds.

The relation R is abstract at the language level.
Its definition is delegated to the verification context.

---

## 5. Constraint Semantics

A FORML constraint is interpreted as a logical formula
over the model function f.

Examples:

### Equality

    output(x) == output(x')

means:

    f(x) = f(x')

---

### Bounded Difference

    |output(x) - output(x')| ≤ ε

means:

    |f(x) - f(x')| ≤ ε

---

### Order

    output(x₁) ≤ output(x₂)

means:

    f(x₁) ≤ f(x₂)

---

### Logical Expressions

Logical operators follow classical propositional logic:

- ∧ (and)
- ∨ (or)
- ¬ (not)
- ⇒ (implication)
- ⇔ (equivalence)

---

## 6. Property Satisfaction

A property is satisfied if its induced logical formula
is true under the chosen interpretation of:

- input domain X
- relation R (if any)
- perturbation model
- arithmetic structure of Y

FORML itself does not decide satisfiability.
It defines the formula to be evaluated.

---

## 7. Backend Independence

FORML semantics is backend-agnostic.

Given a specification S, it defines a formula Φ(S).

A backend is responsible for:

- encoding Φ(S)
- checking satisfiability or validity
- producing certificates or counterexamples

---

## 8. Design Principles

FORML semantics is:

- extensional (defined over function behavior)
- declarative (no execution semantics)
- compositional (complex properties are built from logical primitives)
- independent of verification strategy

A FORML file denotes a set of logical constraints
over a function f.
