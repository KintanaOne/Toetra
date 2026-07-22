# Backend Capabilities

> Status: Stabilizing; target dimensions accepted  
> Scope: Backend-neutral capability declaration and routing

## Purpose

Backend capability declarations allow FORML to reject incompatible verification requests before translation or execution.

A capability model must describe what a backend profile actually supports, not merely identify the backend by name.

---

## Requirement/Capability Principle

Routing succeeds only when:

```text
all task requirements are satisfied by backend capabilities
```

Backend-specific conditionals must not be scattered through IR construction.

---

## Required Capability Dimensions

### Logical

- boolean conjunction/disjunction/negation;
- supported normal forms;
- problem-level predicates;
- native quantifiers when applicable.

### Scalar comparisons

- equality/inequality;
- ordered comparisons;
- supported scalar sorts;
- mixed numeric promotion.

### Arithmetic

- unary numeric signs;
- affine addition/subtraction;
- constant multiplication;
- constant division;
- nonlinear multiplication;
- symbolic division;
- exact rational/real handling where relevant.

### Domains

- interval assumptions;
- open and closed bounds;
- finite-set equality expansion;
- boolean/string/category values;
- symbolic categorical encoding.

### Model and execution

- model assumptions;
- framework-neutral internal model-semantic quantities;
- supported model-constraint families;
- universal-refutation execution;
- existential-witness execution;
- counterexample/witness extraction;
- provenance/trace support.

---

## Target Requirement Shape

The exact API may use booleans, enums or sets, but it must represent distinctions equivalent to:

```text
requires_affine_arithmetic
requires_nonlinear_multiplication
requires_symbolic_division
required_scalar_sorts
requires_finite_set_membership
requires_symbolic_categories
requires_domain_assumptions
requires_model_assumptions
requires_model_semantic_quantities
verification_semantics
normal_form
```

A single `requires_numeric_comparisons` flag does not provide enough information for scalar expressions and typed domains.

---

## Capability Profiles

A backend may expose multiple profiles rather than one overly broad declaration.

Example:

```text
Z3_NUMERIC_AFFINE
Z3_TYPED_CATEGORICAL
Z3_NONLINEAR_EXPERIMENTAL
```

Profiles make support explicit and prevent a partially implemented translator from claiming all theoretical Z3 capabilities.

---

## Minimal Z3 Numeric-Affine Profile

A realistic first profile may declare:

- boolean logic;
- integer/real equality and ordering;
- affine arithmetic;
- numeric interval domains;
- affine model assumptions;
- affine internal model-semantic quantities;
- NNF/CNF/DNF accepted forms;
- universal refutation;
- counterexample extraction.

It must declare `False` for features not yet translated even when the underlying solver could theoretically support them, such as:

- strings;
- enum datatypes;
- categorical finite sets;
- symbolic division;
- nonlinear model families;
- existential result interpretation if the runner does not implement witnesses yet.

---

## Routing Diagnostics

When routing fails, diagnostics should state:

```text
required capability
requested/considered backend profile
unsupported expression or domain source
possible compatible profiles when available
```

Example:

```text
Property requires SYMBOLIC_CATEGORY equality for domain entry x0.region.
Backend profile Z3_NUMERIC_AFFINE supports numeric sorts only.
```

---

## Soundness Rule

A backend capability declaration is a contract.

Over-declaring support is a soundness bug because it allows unsupported or incorrectly encoded properties to pass routing.

Under-declaring support is a completeness/usability issue but does not silently change verification meaning.
