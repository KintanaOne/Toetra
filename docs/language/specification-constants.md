# Specification Constants

> Status: Accepted language contract — implementation pending  
> Scope: User-declared immutable scalar values in a `.forml` header  
> Priority: P0  
> Audience: FORML users, parser authors, semantic maintainers, IR authors, backend authors, test authors

## Purpose

Specification constants let users name reusable business thresholds and scalar values once, then reference them throughout domains and assertions.

```forml
model := "credit-risk.joblib"
target := default_risk

max_risk := 0.20
max_debt_ratio := 0.35
minimum_income := 25000.0
strict_mode := true
preferred_region := "EU"

[LOGIC]:
forall applicant
    with domain(
        applicant.income: [minimum_income, 200000.0],
        applicant.debt: [0.0, 100000.0]
    )
    => target <= max_risk
       AND applicant.debt <= max_debt_ratio * applicant.income
    using Z3
```

They are called **specification constants** because they parameterize the verification specification. They are not symbolic input variables, model features, mutable program variables, or backend solver variables.

---

## Design Goals

Specification constants are intended to make FORML:

- readable for domain experts;
- friendly to users familiar with SQL-like declarative languages;
- auditable, because important thresholds have names;
- maintainable, because one value can be reused across several properties;
- backend-independent, because declarations express specification data rather than solver syntax.

---

## Declaration Syntax

A specification constant is declared in the program header:

```forml
identifier := scalar_literal
```

Canonical formatting uses one declaration per line:

```forml
max_risk := 0.20
minimum_income := 25000.0
strict_mode := true
region_name := "EU"
```

Specification constants appear after the required `model` and `target` declarations, and after the optional `dataset` declaration when one is present. They must appear before the first property section.

The initial declaration profile accepts scalar literals only:

| Literal family | Examples |
|---|---|
| integer | `7`, `25000` |
| real | `0.20`, `3.5`, `-0.1` |
| boolean | `true`, `false` |
| quoted string | `"EU"`, `"high risk"` |

The initial profile does not accept derived declarations:

```forml
annual_limit := monthly_limit * 12
```

Supporting declaration expressions later would require dependency ordering, unknown-reference diagnostics and cycle detection. It is deliberately outside this first contract.

---

## Immutability and Visibility

A specification constant:

- is immutable;
- is visible to every property in the same `.forml` program;
- cannot be redeclared;
- cannot be assigned inside a property or domain;
- is evaluated from its declared literal before backend lowering.

This is invalid:

```forml
max_risk := 0.20
max_risk := 0.30
```

FORML has no assignment statement in property bodies. The `:=` token is declaration syntax only.

---

## Bare-Name Resolution

FORML keeps bare names user-friendly. A scalar expression such as:

```forml
target <= max_risk
```

is resolved semantically rather than requiring a prefix such as `$max_risk`.

### Assertions

In an assertion, a bare identifier is resolved in this order:

1. a specification constant with the same name;
2. otherwise, an implicit feature of the scope's default entity;
3. otherwise, an unbound-name error.

For:

```forml
max_risk := 0.20

[LOGIC]: forall applicant => target <= max_risk
```

`max_risk` denotes the specification constant.

For:

```forml
[LOGIC]: forall applicant => income >= 25000
```

when no `income` specification constant exists, `income` denotes the implicit feature `applicant.income`.

An explicitly qualified reference always denotes a feature:

```forml
max_risk := 0.20

[LOGIC]:
forall applicant
    => applicant.max_risk <= max_risk
```

The left operand is the model feature `applicant.max_risk`; the right operand is the specification constant `max_risk`.

### Domain bounds

Domain subjects remain explicitly qualified:

```forml
applicant.income: [minimum_income, 200000]
```

Bare specification constants are allowed in interval bounds. Bare input-feature fallback is not allowed inside domain bounds; feature references there remain explicit:

```forml
applicant.a: [minimum_value, applicant.b + tolerance]
```

This is rejected when `b` is not a specification constant:

```forml
applicant.a: [b - 1, b + 1]
```

### Finite-set members

In finite-set value position, a bare identifier is resolved in this order:

1. a matching specification constant;
2. otherwise, a symbolic categorical literal.

Example:

```forml
preferred_level := 7

with domain(
    applicant.level: {0, preferred_level}
)
```

When no `EU` specification constant exists, `{EU, US}` continues to denote symbolic categorical literals.

---

## Namespaces and Collisions

The language distinguishes:

| Name kind | Example | Meaning |
|---|---|---|
| specification constant | `max_risk := 0.20` | Immutable scalar value. |
| quantified variable | `forall applicant` | Symbolic input entity. |
| explicit feature | `applicant.income` | Model input feature. |
| implicit feature | `income` | Feature resolved through the default entity. |
| model output | `target` | Output declared by the header. |

Rules:

- reserved words such as `model`, `target`, `dataset`, `domain`, `forall` and `using` cannot be constant names;
- duplicate specification-constant names are rejected;
- a specification constant may share a name with a model feature, because the feature can be explicitly qualified;
- a specification constant must not share a name with a scope variable introduced by `forall`, `exists`, `at`, `check_at` or a pairwise scope;
- FORML rejects such scope/constant collisions rather than applying silent shadowing.

Example of a rejected collision:

```forml
applicant := 7

[LOGIC]: forall applicant => target <= 1
```

---

## Typing

Each specification constant preserves the scalar type of its literal.

```text
7       → INT
0.20    → FLOAT
true    → BOOL
"EU"    → STRING
```

Type compatibility is checked wherever the constant is used.

Valid:

```forml
max_risk := 0.20
[LOGIC]: forall x0 => target <= max_risk
```

Invalid when `target` is numeric:

```forml
max_risk := "low"
[LOGIC]: forall x0 => target <= max_risk
```

The declaration itself is syntactically valid; the incompatible use is a semantic type error.

---

## Initial Profile

The first implementation profile supports:

- header-level immutable scalar declarations;
- integer, real, boolean and quoted-string values;
- references in assertions;
- references in arithmetic expressions;
- references in numeric interval bounds;
- references as finite-set members;
- compile-time substitution while retaining source provenance.

It does not yet support:

- list, set, record or object constants;
- environment-variable interpolation;
- derived constant expressions;
- declaration dependencies;
- local constants scoped to one property;
- mutation or reassignment.

---

## Related Documents

- [Syntax](syntax.md)
- [Grammar](grammar.md)
- [Vocabulary](vocabulary.md)
- [Assertions](assertions.md)
- [Arithmetic Expressions](arithmetic-expressions.md)
- [Domains](domains.md)
- [Normative Examples](examples.md)
- [Invalid and Unsupported Examples](invalid-examples.md)
