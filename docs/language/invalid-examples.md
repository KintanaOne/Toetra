# Invalid and Unsupported Examples

> Status: Accepted diagnostic baseline  
> Scope: Explicit quantified bindings, typed domains, scalar arithmetic and specification constants

## Purpose

This document distinguishes invalid source, invalid semantics, unsupported backend requests and genuine verification outcomes.

```text
invalid syntax ≠ invalid semantics ≠ unsupported capability ≠ violated property
```

Every example has a stable identifier suitable for tests and diagnostics. Every `forml` block below is a complete program. Tests must send the complete program to the public parser/compiler entry point so that failures occur at the documented boundary.

---

## Syntax Rejections

### SYN-Q-001 — Missing Quantified Identifier

```toetra
model := "demo.joblib"
target := score

[LOGIC]: forall => target <= 7
```

Expected boundary: `Source → CST`.

```text
PARSER_QUANTIFIER_IDENTIFIER_REQUIRED
```

### SYN-DOM-001 — Empty Domain Block

```toetra
model := "demo.joblib"
target := score

[LOGIC]: forall x0 with domain() => target <= 7
```

Expected boundary: parser.

```text
PARSER_DOMAIN_REQUIRES_ENTRY
```

### SYN-DOM-002 — Empty Finite Set

```toetra
model := "demo.joblib"
target := score

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

```toetra
model := "demo.joblib"
target := score

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

### SYN-SPC-001 — Non-Literal Declaration Value

```toetra
model := "demo.joblib"
target := score

monthly_limit := 100
annual_limit := monthly_limit * 12

[LOGIC]: forall x0 => target <= annual_limit
```

Expected boundary: parser under the initial specification-constant profile.

```text
PARSER_SPECIFICATION_CONSTANT_LITERAL_REQUIRED
```

Derived declaration expressions are reserved for a later language extension.

---

## Semantic Rejections

### SEM-BIND-001 — Mismatched Quantified Entity

```toetra
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

```toetra
model := "demo.joblib"
target := score

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

```toetra
model := "demo.joblib"
target := score

[LOGIC]:
forall x0
    with domain(y.age: [18, 65])
    => target >= 0
```

```text
SEMANTIC_DOMAIN_ENTITY_MISMATCH
```

### SEM-DOM-003 — Duplicate Domain Subject

```toetra
model := "demo.joblib"
target := score

[LOGIC]:
forall x0
    with domain(
        x0.age: [18, 65],
        x0.age: {21, 42}
    )
    => target >= 0
```

```text
SEMANTIC_DUPLICATE_DOMAIN_SUBJECT
```

### SEM-DOM-004 — Reversed Numeric Interval

```toetra
model := "demo.joblib"
target := score

[LOGIC]:
forall x0
    with domain(x0.age: [65, 18])
    => target >= 0
```

```text
SEMANTIC_INVALID_INTERVAL_ORDER
```

### SEM-DOM-005 — Empty Open Interval

```toetra
model := "demo.joblib"
target := score

[LOGIC]:
forall x0
    with domain(x0.age: ]18, 18[)
    => target >= 0
```

The `[` closes the interval and the final `)` closes `domain(...)`. The syntax is valid, but the represented interval is empty.

```text
SEMANTIC_EMPTY_INTERVAL
```

### SEM-DOM-006 — Target in Domain Bound

```toetra
model := "demo.joblib"
target := score

[LOGIC]:
forall x0
    with domain(x0.a: [0, target])
    => target >= 0
```

```text
SEMANTIC_TARGET_NOT_ALLOWED_IN_DOMAIN
```

### SEM-ARI-001 — Non-Numeric Arithmetic

```toetra
model := "demo.joblib"
target := score

[LOGIC]: forall x0 => x0.region + 1 <= target
```

Assuming `region` is categorical/string-valued:

```text
SEMANTIC_NON_NUMERIC_ARITHMETIC
```

### SEM-ARI-002 — Literal Division by Zero

```toetra
model := "demo.joblib"
target := score

[LOGIC]: forall x0 => x0.a / 0 <= target
```

```text
SEMANTIC_DIVISION_BY_ZERO
```

### SEM-SPC-001 — Duplicate Specification Constant

```toetra
model := "demo.joblib"
target := score

max_risk := 0.20
max_risk := 0.30

[LOGIC]: forall x0 => target <= max_risk
```

```text
SEMANTIC_DUPLICATE_SPECIFICATION_CONSTANT
```

### SEM-SPC-002 — Scope Variable Collision

```toetra
model := "demo.joblib"
target := score

applicant := 7

[LOGIC]: forall applicant => target <= 1
```

```text
SEMANTIC_SPECIFICATION_CONSTANT_SCOPE_COLLISION
```

FORML rejects this collision rather than silently shadowing either declaration.

### SEM-SPC-003 — Incompatible Constant Use

```toetra
model := "demo.joblib"
target := score

max_score := "high"

[LOGIC]: forall x0 => target <= max_score
```

Assuming a numeric target:

```text
SEMANTIC_INCOMPATIBLE_SPECIFICATION_CONSTANT_TYPE
```

### SEM-SPC-004 — Bare Domain Feature Is Not Implicit

```toetra
model := "demo.joblib"
target := score

[LOGIC]:
forall x0
    with domain(
        x0.a: [b - 1, b + 1]
    )
    => target >= 0
```

When no specification constant named `b` exists:

```text
SEMANTIC_UNBOUND_DOMAIN_NAME
```

Domain bounds do not fall back to implicit feature resolution. Write `x0.b` explicitly.

### SEM-SPC-005 — Reserved Specification-Constant Name

```toetra
model := "demo.joblib"
target := score

domain := 7

[LOGIC]: forall x0 => target <= 7
```

Depending on tokenization, this may be rejected at the parser boundary; otherwise semantic registration must reject it. The canonical diagnostic family is:

```text
SPECIFICATION_CONSTANT_RESERVED_NAME
```

---

## Valid but Backend-Unsupported Requests

These complete programs must pass parser, builder and semantic validation before capability matching rejects them.

### UNSUP-ARI-001 — Symbolic Product

```toetra
model := "demo.joblib"
target := score

[LOGIC]: forall x0 => x0.a * x0.b <= target using Z3
```

For an affine-only backend profile:

```text
BACKEND_UNSUPPORTED_NONLINEAR_ARITHMETIC
```

### UNSUP-ARI-002 — Symbolic Denominator

```toetra
model := "demo.joblib"
target := score

[LOGIC]: forall x0 => x0.a / x0.b <= target using Z3
```

```text
requires_symbolic_division = true
BACKEND_UNSUPPORTED_SYMBOLIC_DIVISION
```

### UNSUP-DOM-001 — Symbolic Categories Without Encoding Capability

```toetra
model := "demo.joblib"
target := score

[LOGIC]:
forall x0
    with domain(x0.region: {EU, US})
    => target <= 7
    using Z3
```

```text
BACKEND_UNSUPPORTED_CATEGORICAL_DOMAIN
```

### UNSUP-SPC-001 — String Constant Reaches Numeric-Only Categorical Backend

```toetra
model := "demo.joblib"
target := score

preferred_region := "EU"

[LOGIC]:
forall x0
    with domain(x0.region: {preferred_region, US})
    => target <= 7
    using Z3
```

The language and semantic layers accept the request. A backend without string/categorical encoding reports:

```text
BACKEND_UNSUPPORTED_CATEGORICAL_DOMAIN
```

---

## Verification Outcomes Are Not Compilation Failures

### Universal SAT

For universal refutation, `Γ ∧ ¬P = SAT` means `COUNTEREXAMPLE`.

### Universal UNSAT

`Γ ∧ ¬P = UNSAT` means `VERIFIED`, subject to non-vacuity checks.

### Existential SAT

`Γ ∧ P = SAT` means `WITNESS`.

### Existential UNSAT

`Γ ∧ P = UNSAT` means `NO_WITNESS`.

### Empty Admissible Domain

A universal property can appear proved because `Γdomain ∧ Γmodel` is unsatisfiable. FORML should emit:

```text
VERIFICATION_VACUOUS_EMPTY_DOMAIN
```

## Related Documents

- [Normative Examples](examples.md)
- [Specification Constants](specification-constants.md)
- [Domains](domains.md)
- [Arithmetic Expressions](arithmetic-expressions.md)
- [Backend Diagnostics](../backends/diagnostics.md)
- [Language Evolution Test Matrix](../testing/language-evolution-test-matrix.md)
