# Quantified Variable Bindings

> Status: Target language contract — implementation pending  
> Scope: Explicit variables introduced by `forall` and `exists`  
> Priority: P0  
> Audience: DSL users, parser authors, semantic maintainers, IR authors, test authors

## Purpose

This document defines how quantified scopes introduce and bind variables in FORML.

The target syntax is:

```forml
forall <identifier>
exists <identifier>
```

Unicode aliases may also be accepted:

```forml
∀ <identifier>
∃ <identifier>
```

The identifier is part of the user-visible language. FORML must preserve it from the CST through semantic validation and into `ScopeIR`.

---

## Core Decision

A quantified scope introduces exactly one explicitly named symbolic input variable.

```forml
forall x0 => target <= 7
```

creates the semantic binding:

```text
x0: symbolic
```

and the default entity:

```text
x0
```

FORML must not replace this name with an implicit internal variable such as `_x`.

---

## Universal Quantification

```forml
forall x0 => assertion
```

means:

```text
For every admissible valuation of x0, assertion must hold.
```

When a domain is present:

```forml
forall x0
    with domain(
        x0.age: [18, 65]
    )
    => target <= 7
```

only valuations of `x0` satisfying the domain participate in the property.

The exact syntax and lowering rules for intervals and finite sets are defined in [Domains](domains.md).

---

## Existential Quantification

```forml
exists x0 => assertion
```

means:

```text
There exists at least one admissible valuation of x0 for which assertion holds.
```

This document defines the language meaning. A backend may still reject the request when existential quantification is not part of its declared capabilities.

---

## Explicit Input References

An explicit input reference names its entity:

```forml
x0.age >= 18
```

Inside a scope introduced by `forall x0` or `exists x0`, every explicit input entity must resolve to the declared identifier.

Valid:

```forml
forall x0 => x0.age >= 18
```

Invalid:

```forml
forall x0 => y.age >= 18
```

The invalid example must fail during semantic binding. FORML must not silently reinterpret `y.age` as `x0.age`, even though the scope contains only one symbolic input variable.

---

## Implicit Input References

A feature reference without an explicit entity uses the quantified variable as its default entity.

```forml
forall x0 => age >= 18
```

is resolved semantically as:

```text
x0.age >= 18
```

This shorthand does not remove the explicit binding from the scope. It only uses the scope's `default_entity` rule.

---

## Model Output References

`target` is not an input entity. It refers to the model output declared in the header.

Therefore this property is valid:

```forml
forall x0 => target <= 7
```

The quantified identifier does not need to appear textually in the assertion. The model assumptions connect the output to the quantified input:

```text
Model(x0, target)
```

A target-only assertion is still quantified over `x0` once it is combined with domain and model assumptions.

---

## Domain Binding

A domain attached to a single-variable quantified scope may constrain only that declared input variable.

Valid:

```forml
forall x0
    with domain(
        x0.age: [18, 65],
        x0.region: {EU, US}
    )
    => target <= 7
```

Invalid entity mismatch:

```forml
forall x0
    with domain(
        y.age: [18, 65]
    )
    => target <= 7
```

Invalid implicit domain subject:

```forml
forall x0
    with domain(
        age: [18, 65]
    )
    => target <= 7
```

Unlike assertions, domains require explicit subject qualification. This is intentional: a domain is a declaration-like admissibility block and should remain unambiguous when multi-variable scopes are added later.

For the initial language scope, one quantified property introduces one symbolic input variable. Multi-variable quantification is deferred.

---

## Binding Rules

For a quantified scope `Q x0`, semantic binding follows these rules:

1. Register `x0` in the symbol table with role `symbolic`.
2. Set `x0` as the default entity for implicit input feature references.
3. Resolve explicit `x0.feature` references to the registered symbol.
4. Reject explicit input references whose entity is not registered.
5. Require every domain subject to be explicitly qualified.
6. Reject domain entries whose subject uses another input entity.
7. Reject `target` as a domain subject.
8. Resolve `target` independently as the model output reference in assertions.
9. Do not apply a single-variable alias fallback to unknown explicit entities.

The ninth rule is important. Concise implicit references are supported, but misspelled or foreign explicit entities must remain errors.

---

## Valid Examples

```forml
[BOUND]: forall x0 => target <= 7
```

```forml
[LOGIC]: forall applicant => applicant.age >= 18 -> target == true
```

```forml
[BOUND]: exists candidate => candidate.score > 0
```

```forml
[BOUND]: forall x0 => age >= 18
```

The last example resolves `age` to `x0.age`.

---

## Invalid Examples

### Missing quantified identifier

```forml
[BOUND]: forall => target <= 7
```

Expected failure boundary:

```text
parser
```

### Explicit entity mismatch

```forml
[BOUND]: forall x0 => x1.age >= 18
```

Expected failure boundary:

```text
semantic binding
```

### Domain entity mismatch

```forml
[BOUND]: forall x0
    with domain(
        x1.age: [18, 65]
    )
    => target <= 7
```

Expected failure boundary:

```text
semantic binding or domain validation
```

---

## Target Artifact Shapes

### AST

```text
QuantifierExprNode(
    quantifier="forall",
    variable="x0",
    domain=...
)
```

### SemanticContext

```text
type = quantifier
quantifier = forall
variables = {
    "x0": "symbolic"
}
default_entity = "x0"
```

### ScopeIR

```text
kind = quantifier
variables = {
    "x0": "symbolic"
}
```

The original identifier must remain traceable across all three artifacts.

---

## Deferred Features

This decision does not yet define:

- multiple variables in one quantifier;
- nested quantifiers;
- variable shadowing;
- quantifier alternation;
- backend support for first-order quantifier objects;
- existential proof and witness reporting.

These features require separate decisions and tests.

---

## Required Test Families

```text
parser_accepts_forall_identifier
parser_accepts_exists_identifier
parser_rejects_missing_quantified_identifier
builder_preserves_quantified_identifier
semantic_registers_declared_symbolic_variable
semantic_uses_quantified_variable_as_default_entity
semantic_accepts_matching_explicit_entity
semantic_rejects_mismatched_explicit_entity
semantic_rejects_mismatched_domain_entity
semantic_rejects_implicit_domain_subject
semantic_preserves_domain_boundary_kinds
target_reference_does_not_require_textual_input_reference
ir1_preserves_quantified_identifier
```

---

## Related Documents

- [Scopes](scopes.md)
- [Domains](domains.md)
- [Syntax](syntax.md)
- [Grammar](grammar.md)
- [Assertions](assertions.md)
- [AST to Semantic Contract](../contracts/ast-to-semantic.md)
- [Scope IR](../ir/scope-ir.md)
