
# Invalid and Unsupported Examples

> Status: Accepted diagnostic baseline  
> Scope: Explicit quantified bindings, typed domains and scalar arithmetic

## Purpose

This document distinguishes invalid source, invalid semantics, unsupported backend requests and genuine verification outcomes.

```text
invalid syntax ≠ invalid semantics ≠ unsupported capability ≠ violated property
```

Every example has a stable identifier suitable for tests and diagnostics.

Unless a complete header is shown, property-only snippets assume this valid common header:

```forml
model := "demo.joblib"
target := score
```

Tests must assemble a complete program so that rejection occurs at the intended boundary.

---

## Syntax Rejections

### SYN-Q-001 — Missing Quantified Identifier

```forml
model := "demo.joblib"
target := score

[LOGIC]: forall => target <= 7
```

Expected boundary:

```text
Source → CST
```

Expected diagnostic family:

```text
PARSER_QUANTIFIER_IDENTIFIER_REQUIRED
```

The default target grammar requires an identifier after `forall` and `exists`.

### SYN-DOM-001 — Empty Domain Block

```forml
[LOGIC]: forall x0 with domain() => target <= 7
```

Expected boundary: parser.

```text
PARSER_DOMAIN_REQUIRES_ENTRY
```

### SYN-DOM-002 — Empty Finite Set

```forml
[LOGIC]:
forall x0
    with domain(x0.region: {})
    => target <= 7
```

Expected boundary: parser.

```text
PARSER_FINITE_SET_REQUIRES_VALUE
```

### SYN-DOM-003 — Unsupported Parenthesis Interval Notation

```forml
[LOGIC]:
forall x0
    with domain(x0.age: (18, 65])
    => target <= 7
```

Expected boundary: parser.

FORML uses bracket-only French interval notation:

```text
[a, b]   ]a, b]   [a, b[   ]a, b[
```

```text
PARSER_INVALID_INTERVAL_DELIMITER
```

---

## Semantic Rejections

### SEM-BIND-001 — Mismatched Quantified Entity

```forml
model := "demo.joblib"
target := score

[BOUND]: forall x0 => candidate.age >= 18
```

Expected boundary: semantic binding.

```text
SEMANTIC_UNBOUND_QUANTIFIED_ENTITY
```

The compiler must not alias `candidate` to `x0` merely because only one variable is declared.

### SEM-DOM-001 — Implicit Domain Subject

```forml
[LOGIC]:
forall x0
    with domain(age: [18, 65])
    => target >= 0
```

Expected boundary: semantic domain validation.

```text
SEMANTIC_DOMAIN_SUBJECT_MUST_BE_EXPLICIT
```

Assertions may use an implicit default entity. Domain subjects may not.

### SEM-DOM-002 — Subject Bound to Another Entity

```forml
[LOGIC]:
forall x0
    with domain(y.age: [18, 65])
    => target >= 0
```

Expected diagnostic:

```text
SEMANTIC_DOMAIN_ENTITY_MISMATCH
```

### SEM-DOM-003 — Duplicate Domain Subject

```forml
[LOGIC]:
forall x0
    with domain(
        x0.age: [18, 65],
        x0.age: {21, 42}
    )
    => target >= 0
```

Expected diagnostic:

```text
SEMANTIC_DUPLICATE_DOMAIN_SUBJECT
```

### SEM-DOM-004 — Reversed Numeric Interval

```forml
[LOGIC]:
forall x0
    with domain(x0.age: [65, 18])
    => target >= 0
```

Expected diagnostic:

```text
SEMANTIC_INVALID_INTERVAL_ORDER
```

### SEM-DOM-005 — Empty Open Interval

```forml
[LOGIC]:
forall x0
    with domain(x0.age: ]18, 18[)
    => target >= 0
```

The `[` closes the open interval and the final `)` closes the `domain(...)` call. The syntax is valid, but the represented interval is empty and is rejected semantically:

```text
SEMANTIC_EMPTY_INTERVAL
```

### SEM-DOM-006 — Target in Domain Bound

```forml
[LOGIC]:
forall x0
    with domain(x0.a: [0, target])
    => target >= 0
```

Expected diagnostic:

```text
SEMANTIC_TARGET_NOT_ALLOWED_IN_DOMAIN
```

Domain assumptions constrain model inputs. They must not depend on the model output in the initial language contract.

### SEM-ARI-001 — Non-Numeric Arithmetic

```forml
[LOGIC]: forall x0 => x0.region + 1 <= target
```

Assuming `region` is categorical/string-valued, expected diagnostic:

```text
SEMANTIC_NON_NUMERIC_ARITHMETIC
```

### SEM-ARI-002 — Literal Division by Zero

```forml
[LOGIC]: forall x0 => x0.a / 0 <= target
```

Expected diagnostic:

```text
SEMANTIC_DIVISION_BY_ZERO
```

---

## Valid but Backend-Unsupported Requests

These examples must pass parser, builder and semantic validation.

### UNSUP-ARI-001 — Symbolic Product

```forml
[LOGIC]: forall x0 => x0.a * x0.b <= target using Z3
```

For an affine-only backend profile:

```text
BACKEND_UNSUPPORTED_NONLINEAR_ARITHMETIC
```

### UNSUP-ARI-002 — Symbolic Denominator

```forml
[LOGIC]: forall x0 => x0.a / x0.b <= target using Z3
```

Expected capability requirement:

```text
requires_symbolic_division = true
```

Possible diagnostic:

```text
BACKEND_UNSUPPORTED_SYMBOLIC_DIVISION
```

The initial affine profile rejects symbolic denominators before execution; it does not approximate their semantics.

### UNSUP-DOM-001 — Symbolic Categories Without Encoding Capability

```forml
[LOGIC]:
forall x0
    with domain(x0.region: {EU, US})
    => target <= 7
    using Z3
```

If the registered Z3 profile supports numeric variables only:

```text
BACKEND_UNSUPPORTED_CATEGORICAL_DOMAIN
```

---

## Verification Outcomes Are Not Compilation Failures

### Universal SAT

For universal refutation:

```text
Γ ∧ ¬P = SAT
```

Meaning:

```text
counterexample found
```

### Universal UNSAT

```text
Γ ∧ ¬P = UNSAT
```

Meaning:

```text
property verified, subject to non-vacuity checks
```

### Existential SAT

```text
Γ ∧ P = SAT
```

Meaning:

```text
witness found
```

### Existential UNSAT

```text
Γ ∧ P = UNSAT
```

Meaning:

```text
no admissible witness exists
```

### Empty Admissible Domain

A universal property can appear proved because `Γdomain ∧ Γmodel` is unsatisfiable.

FORML should emit a distinct warning such as:

```text
VERIFICATION_VACUOUS_EMPTY_DOMAIN
```

## Related Documents

- [Normative Examples](examples.md)
- [Domains](domains.md)
- [Arithmetic Expressions](arithmetic-expressions.md)
- [Backend Diagnostics](../backends/diagnostics.md)
- [Language Evolution Test Matrix](../testing/language-evolution-test-matrix.md)
