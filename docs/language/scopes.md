# Scopes

> Status: Target language contract — implementation partially available  
> Scope: Evaluation scopes, variable introduction, and semantic contexts  
> Priority: P0  
> Audience: DSL users, semantic layer contributors, IR authors, test authors

## Purpose

Scopes define where a FORML property is evaluated.

They form the left-hand side of a property rule:

```forml
[PROPERTY]: scope => assertion
```

A scope introduces variables and semantic roles. It may also attach a neighborhood or a domain. During compilation, scope syntax becomes a `SemanticContext`, then a `ScopeIR`.

---

## Scope Responsibilities

A scope defines:

| Responsibility | Example |
|---|---|
| Declared variables | `x`, `x'`, `x0` |
| Semantic roles | anchor, perturbation, symbolic |
| Default entity | implicit `age` resolves to the scope's default variable |
| Neighborhood | `L2` ball with `eps=0.1` |
| Domain | admissible valuations for a symbolic variable |
| Semantic scope kind | pointwise, local, pairwise, quantifier |

A scope does not define the model output. The keyword `target` refers to the output declared in the program header.

---

## `check_at` Scope

### Syntax

```forml
[BOUND]: check_at x0 => target >= 0
```

### Meaning

`check_at` evaluates a property for one concrete point identified by `x0`.

Semantic context:

| Variable | Role |
|---|---|
| `x0` | anchor |

Default entity:

```text
x0
```

Therefore:

```forml
age >= 18
```

resolves to:

```text
x0.age >= 18
```

`check_at` is not a domain-wide scope. The concrete values associated with `x0` must come from an execution context, observation, dataset row, or future binding mechanism. A domain does not transform `check_at` into universal quantification.

### Typical Use Cases

- checking one known observation;
- pointwise model diagnostics;
- deterministic regression tests;
- validating a concrete counterexample candidate.

---

## `at` Scope

### Syntax

```forml
[ROBUSTNESS]: at x in neighborhood(metric=L2, eps=0.1) => CLASSIFICATION.EQUAL()
```

### Meaning

`at` introduces an anchor point and an implicit perturbation variable.

Semantic context:

| Variable | Role |
|---|---|
| `x` | anchor |
| `x'` | perturbation |

Default entity:

```text
x'
```

Thus an implicit feature reference such as:

```forml
age <= 30
```

is resolved to:

```text
x'.age <= 30
```

### Typical Use Cases

- local robustness;
- stability under perturbation;
- neighborhood-constrained counterexample search.

---

## Pairwise Scope

### Syntax

```forml
[MONOTONICITY]: x ~ x' in neighborhood(metric=L1, eps=1.0) => x'.score >= x.score
```

### Meaning

Pairwise scope compares two explicitly named related inputs.

Semantic context:

| Variable | Role |
|---|---|
| `x` | anchor |
| `x'` | perturbation or paired point |

The current pair convention requires the right identifier to be the primed form of the left identifier.

Valid:

```text
x ~ x'
```

Invalid under the current contract:

```text
x ~ y
```

Unrelated or independently bound pairs require a future language decision.

---

## Quantified Scopes

### Target Syntax

```forml
[BOUND]: forall x0 => target <= 7
```

```forml
[BOUND]: exists candidate => candidate.score > 0
```

Unicode aliases may be accepted:

```forml
[BOUND]: ∀ x0 => target <= 7
```

```forml
[BOUND]: ∃ candidate => candidate.score > 0
```

### Meaning

A quantified scope introduces one explicitly named symbolic input variable.

For:

```forml
forall x0
```

the semantic context is:

```text
quantifier = forall
variables = {
    "x0": "symbolic"
}
default_entity = "x0"
```

FORML must preserve the declared identifier. It must not replace it with an implicit internal name such as `_x`.

### Universal Quantifier

```forml
forall x0 => assertion
```

means that `assertion` must hold for every admissible valuation of `x0`.

### Existential Quantifier

```forml
exists x0 => assertion
```

means that at least one admissible valuation of `x0` must satisfy `assertion`.

The language meaning is independent from backend availability. A backend may reject a quantified request when its capabilities do not support the required semantics.

---

## Quantified Binding Rules

Inside `forall x0` or `exists x0`:

- `x0.age` is a valid explicit input reference;
- `age` is a valid implicit reference and resolves to `x0.age`;
- `y.age` is invalid unless `y` is separately declared by a future multi-variable scope;
- `target` remains valid because it is a model-output reference, not an input entity.

Valid:

```forml
[BOUND]: forall x0 => x0.age >= 18
```

Valid with implicit input binding:

```forml
[BOUND]: forall x0 => age >= 18
```

Valid target-only assertion:

```forml
[BOUND]: forall x0 => target <= 7
```

Invalid explicit binding:

```forml
[BOUND]: forall x0 => y.age >= 18
```

An unknown explicit entity must be rejected. The semantic layer must not silently alias `y` to `x0` merely because the scope contains one variable.

The complete normative rules are defined in [Quantified Variable Bindings](quantified-bindings.md).

---

## Domains on Quantified Scopes

A quantified variable may be restricted by a typed domain:

```forml
[LOGIC]:
forall x0
    with domain(
        x0.age: [18, 65],
        x0.region: {EU, US}
    )
    => target <= 7
```

Domain subjects are always explicitly qualified. Every subject entity must be declared by the scope.

Valid:

```forml
forall x0
    with domain(
        x0.age: [18, 65]
    )
    => target <= 7
```

Invalid:

```forml
forall x0
    with domain(
        y.age: [18, 65]
    )
    => target <= 7
```

The domain contributes admissibility assumptions. It does not replace the quantifier and does not turn `check_at` into a domain-wide scope.

Multiple domain entries are conjunctive. Intervals preserve open/closed boundary kinds, and braces denote finite discrete sets. The full contract is defined in [Domains](domains.md).

---

## Neighborhoods

Neighborhoods define perturbation constraints for scopes such as `at` and pairwise scopes.

Example:

```forml
in neighborhood(metric=L2, eps=0.1)
```

Expected semantic representation:

```text
metric: L2
eps: 0.1
args: {...}
```

Neighborhoods later participate in:

- `SemanticContext`;
- `ScopeIR`;
- assertion aggregation;
- backend lowering.

---

## Scope to SemanticContext

| Scope Syntax | Semantic Scope | Variables | Default Entity |
|---|---|---|---|
| `check_at x0` | pointwise | `{x0: anchor}` | `x0` |
| `at x` | local | `{x: anchor, x': perturbation}` | `x'` |
| `x ~ x'` | pairwise | `{x: anchor, x': perturbation}` | `x'` |
| `forall x0` | quantifier | `{x0: symbolic}` | `x0` |
| `exists x0` | quantifier | `{x0: symbolic}` | `x0` |

---

## Scope to IR

`ScopeIR` must preserve:

- scope kind;
- the exact declared variable names;
- variable roles;
- quantifier kind when applicable;
- neighborhood metadata;
- domain metadata;
- enough provenance for diagnostics and backend routing.

Conceptual quantified `ScopeIR`:

```text
kind: quantifier
variables:
  x0: symbolic
quantifier: forall
domain: ...
```

---

## Current and Target Behavior

| Area | Current implementation | Target contract |
|---|---|---|
| `check_at`, `at`, pairwise scopes | available | retained |
| word and Unicode quantifiers | partially available | retained and normalized |
| explicit quantified identifier | not yet represented end-to-end | required |
| implicit `_x` convention | present in older documentation/implementation | removed from the public contract |
| strict mismatch rejection | current single-variable fallback may interfere | required for explicit quantified references |
| quantified backend execution | backend-dependent | capability-gated |

---

## Testing Requirements

```text
check_at_introduces_anchor
at_introduces_anchor_and_perturbation
pairwise_preserves_both_identifiers
forall_requires_identifier
exists_requires_identifier
quantifier_preserves_declared_identifier
quantifier_sets_declared_identifier_as_default_entity
matching_explicit_reference_is_accepted
implicit_reference_resolves_to_declared_identifier
mismatched_explicit_reference_is_rejected
target_only_assertion_is_accepted
mismatched_domain_subject_is_rejected
implicit_domain_subject_is_rejected
domain_interval_boundaries_are_preserved
domain_finite_set_values_are_preserved
scope_ir_preserves_quantified_identifier
```

---

## Related Documents

- [Quantified Variable Bindings](quantified-bindings.md)
- [Domains](domains.md)
- [Properties](properties.md)
- [Assertions](assertions.md)
- [Syntax](syntax.md)
- [Grammar](grammar.md)
- [IR Scope](../ir/scope-ir.md)
- [AST to Semantic Contract](../contracts/ast-to-semantic.md)
