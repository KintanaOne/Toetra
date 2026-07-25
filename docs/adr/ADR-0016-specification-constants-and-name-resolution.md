# ADR-0016 — Use Specification Constants and Context-Aware Bare-Name Resolution

> Status: Accepted  
> Date: 2026-07  
> Scope: Language semantics, symbol resolution, AST and IR lowering

## Context

FORML already allows header declarations using `identifier := value`, but those declarations had no stable architectural meaning across the compiler pipeline.

The language also allows bare identifiers inside scalar expressions:

```toetra
[LOGIC]: forall applicant => income >= minimum_income
```

A bare identifier may denote either:

- a reusable value declared by the user;
- or an implicit feature of the current scope entity.

Requiring a sigil such as `$minimum_income` would remove the ambiguity, but would make the DSL less natural for domain experts. FORML aims for a declarative surface closer to SQL than to solver syntax.

A compiler decision is therefore required for:

- the public name of user-declared values;
- raw AST representation of unresolved names;
- semantic lookup order;
- collision handling;
- domain-specific lookup rules;
- IR lowering and provenance.

## Decision

FORML calls user-declared immutable scalar values **specification constants**.

Initial syntax:

```toetra
max_risk := 0.20
minimum_income := 25000.0
strict_mode := true
region := "EU"
```

The initial profile accepts scalar literals only. Derived declarations such as `annual_limit := monthly_limit * 12` are deferred.

### Raw AST

The builder preserves declarations explicitly:

```text
HeaderNode(
    model,
    target,
    specification_constants,
)

SpecificationConstantDeclarationNode(name, value)
```

A bare scalar name is represented as an unresolved `NameRefNode`. The builder must not guess whether it is a specification constant or an implicit feature.

### Semantic resolution

In assertion scalar-expression position, a bare name is resolved in this order:

1. matching specification constant;
2. implicit feature of the scope's default entity;
3. unbound-name error.

An explicitly qualified reference such as `applicant.threshold` always denotes a feature.

In domain interval bounds:

1. a bare matching specification constant is allowed;
2. feature references must be explicit;
3. an unmatched bare name is an error.

In finite-set value position:

1. a matching specification constant is used;
2. otherwise the bare identifier denotes a symbolic categorical literal.

### Collisions

FORML rejects:

- duplicate specification-constant declarations;
- reserved words as declaration names;
- a specification constant sharing a name with a scope variable introduced by `forall`, `exists`, `at`, `check_at` or pairwise syntax.

A specification constant may share a name with a feature because the feature can be explicitly qualified.

### IR lowering

After semantic resolution, a specification-constant reference is lowered as a typed constant expression, not as a solver variable.

IR must preserve provenance equivalent to:

```text
value = 0.20
dtype = FLOAT
source_kind = SPECIFICATION_CONSTANT
source_name = max_risk
```

A backend may encode the literal directly. It must not create an unconstrained symbolic variable for the specification constant.

## Rationale

This decision preserves a user-friendly declarative syntax while keeping compiler boundaries explicit.

It provides:

- named business thresholds;
- centralized specification values;
- readable policies;
- deterministic name resolution;
- explicit feature disambiguation;
- backend-independent constant semantics;
- traceable diagnostics and proof output.

`NameRefNode` is necessary because resolving names in the builder would mix syntax construction with semantic symbol lookup.

## Consequences

### Positive

- Toetra specifications become easier to read and audit.
- The same value can be reused across properties and domains.
- Bare names remain concise.
- Explicit feature qualification removes ambiguity when names overlap.
- Constants do not pollute solver models as symbolic variables.
- Provenance can connect diagnostics back to the declared business name.

### Negative

- Bare-name resolution becomes context-sensitive.
- The semantic layer needs a program-level declaration table before property validation.
- Raw AST must distinguish `NameRefNode` from `AttributeNode`.
- Domain finite-set positions require a specific resolution rule.
- Collision diagnostics become part of the language contract.

## Alternatives considered

### Prefix specification constants with a sigil

Example: `$max_risk`.

Rejected because it adds syntax noise and weakens the SQL-like declarative goal.

### Resolve every bare name as an implicit feature

Rejected because specification constants would require a separate verbose syntax and existing declaration syntax would remain underused.

### Resolve names in the builder

Rejected because the builder does not own symbol tables, scope defaults or semantic lookup.

### Encode constants as backend variables

Rejected because specification constants are immutable known values, not unknowns to solve for.

### Allow silent shadowing between constants and scope variables

Rejected because it makes properties difficult to audit and can silently change meaning.

## Impact on FORML

This decision affects:

- header parsing and AST construction;
- program-level symbol registration;
- scalar-expression binding;
- domain-bound and finite-set resolution;
- type validation;
- IR1 constant lowering;
- provenance and diagnostics;
- parser, builder, semantic, IR and end-to-end tests.

Implementation must proceed through the documented gates. The language contract is accepted before code support is claimed.
