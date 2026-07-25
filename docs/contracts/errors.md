# Error Boundaries Contract

> Status: P0 / Accepted target taxonomy  
> Scope: Failure ownership across the language and verification pipeline  
> Audience: maintainers, diagnostic authors, testers and Miova campaign authors

## Purpose

A failure is useful only when Toetra reports the correct owning boundary and preserves the original cause.

---

## Boundary Families

| Boundary | Error family | New feature examples |
|---|---|---|
| Source → CST | Parser/Syntax | missing quantified identifier, malformed interval |
| CST → AST | Builder/Structure | missing scalar operand, unrepresentable domain entry |
| AST → Semantic | Binding/Type/Domain | `forall x0` with `y.a`, invalid arithmetic types |
| Semantic → IR1 | IR lowering contract | lost resolved symbol, lost quantifier kind |
| IR1 → IR2 | Normalization/Assumption | invalid DOMAIN assumption provenance |
| Aggregation | Composition | existential property negated as universal |
| Routing | Compatibility | no backend supports symbolic division |
| Backend compilation | Encoding | unsupported sort or categorical encoding |
| Runtime | Solver execution/result | solver failure or semantics-inconsistent result |

---

## Required Diagnostic Fields

A structured diagnostic should expose when available:

- stable code;
- owning boundary/layer;
- human-readable message;
- property identity;
- source span;
- offending identifier/operator/domain entry;
- expected declaration/type/capability;
- actual declaration/type/capability;
- causal exception;
- provenance chain;
- expected-vs-unexpected classification for mutation campaigns.

---

## Recommended Diagnostic Codes

Exact exception class names remain implementation choices, but stable diagnostics should cover:

```text
PARSER_MISSING_QUANTIFIED_IDENTIFIER
PARSER_INVALID_INTERVAL_DELIMITERS
BUILDER_MALFORMED_SCALAR_EXPRESSION
BUILDER_MALFORMED_DOMAIN_ENTRY
SEMANTIC_UNBOUND_EXPLICIT_ENTITY
SEMANTIC_QUANTIFIED_ENTITY_MISMATCH
SEMANTIC_IMPLICIT_DOMAIN_SUBJECT
SEMANTIC_DUPLICATE_DOMAIN_SUBJECT
SEMANTIC_TARGET_IN_INPUT_DOMAIN
SEMANTIC_EMPTY_INTERVAL
SEMANTIC_INCOMPATIBLE_SET_MEMBER
SEMANTIC_NON_NUMERIC_ARITHMETIC
SEMANTIC_LITERAL_DIVISION_BY_ZERO
IR1_MISSING_RESOLVED_REFERENCE
IR1_LOST_QUANTIFIER_KIND
IR2_INVALID_DOMAIN_ASSUMPTION
AGGREGATION_INVALID_VERIFICATION_SEMANTICS
BACKEND_UNSUPPORTED_AFFINE_ARITHMETIC
BACKEND_UNSUPPORTED_NONLINEAR_ARITHMETIC
BACKEND_UNSUPPORTED_SYMBOLIC_DIVISION
BACKEND_UNSUPPORTED_SCALAR_SORT
BACKEND_UNSUPPORTED_CATEGORY_ENCODING
```

---

## Binding Diagnostic Example

For:

```toetra
forall x0 => y.a <= 3
```

Toetra should report conceptually:

```text
Explicit entity `y` is not declared by quantified scope `forall x0`.
Expected entity: x0.
Implicit feature syntax `a` may be used when the default entity is intended.
```

It must not silently reinterpret `y.a` as `x0.a`.

---

## Capability Diagnostic Example

For a meaningful but unsupported expression:

```toetra
forall x0 => x0.a * x0.b <= target
```

the diagnostic belongs to requirement/routing/backend compatibility, not parsing or semantic typing:

```text
The property requires nonlinear multiplication.
Requested backend Z3 profile declares affine arithmetic only.
```

---

## Expected Failure Semantics

| Classification | Meaning |
|---|---|
| Expected rejection | Invalid artifact rejected at its owning boundary. |
| Wrong-boundary rejection | Invalid artifact rejected, but contract ownership is violated. |
| False rejection | Valid artifact rejected. |
| False acceptance | Invalid artifact reaches a later layer. |
| Internal failure | Unclassified exception, assertion crash or corrupted state. |

Miova campaigns should distinguish all five.

## Specification Constant Diagnostics

The semantic/type boundary owns diagnostics for:

- duplicate specification-constant declarations;
- reserved declaration names;
- collisions with scope variables;
- unresolved bare names;
- incompatible constant uses;
- unsupported declaration literal kinds.

A parser error is appropriate only when declaration syntax is malformed. A backend-capability diagnostic is appropriate when the constant is semantically valid but its type cannot be encoded by the selected backend profile.
