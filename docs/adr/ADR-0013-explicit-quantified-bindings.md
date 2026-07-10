# ADR-0013 — Use Explicitly Bound Quantified Variables

> Status: Accepted  
> Date: 2026-07  
> Scope: DSL scopes, semantic binding, and quantified verification

## Context

FORML supports quantified properties intended to describe behavior over a symbolic input space.

An implicit compiler-generated variable such as `_x` makes short examples possible, but it hides an important part of the user's intent and weakens diagnostics. In particular, an implementation that silently aliases an unknown explicit entity to the only variable in scope can accept misspelled or inconsistent properties.

The language must distinguish clearly between:

- a concrete point introduced by `check_at`;
- a symbolic input introduced by a quantifier;
- an implicit feature reference resolved through the current scope;
- an explicit feature reference that must name an actually declared entity;
- the model output reference `target`, which is not an input variable.

The target quantified syntax is:

```forml
forall x0 => target <= 7
```

and:

```forml
exists candidate => candidate.score > 0
```

## Decision

FORML quantifiers bind an explicit identifier.

The normative forms are:

```text
forall <identifier>
exists <identifier>
```

For a quantified scope `Q x0`, the compiler must:

1. register `x0` in the semantic symbol table with the role `symbolic`;
2. preserve the exact source identifier in AST, semantic context, IR scope, diagnostics, and traces;
3. set `x0` as the default entity for implicit input-feature references in the assertion;
4. resolve `x0.feature` only against the declared `x0` symbol;
5. reject an explicit input reference such as `y.feature` when `y` is not declared by the scope;
6. prohibit the single-variable alias fallback for unknown explicit entities;
7. require domain subjects to be explicitly qualified by the declared identifier;
8. resolve `target` independently as the model output declared by the program header.

Therefore:

```forml
forall x0 => age >= 18
```

is valid and resolves `age` to `x0.age`, while:

```forml
forall x0 => y.age >= 18
```

is invalid and must not be reinterpreted as `x0.age`.

A quantified variable does not need to appear textually in the assertion. This remains valid:

```forml
forall x0 => target <= 7
```

because model assumptions connect the symbolic input `x0` to the model output.

### Quantifier meaning

The language-level meaning of:

```forml
forall x0 with domain(...) => P
```

is:

```text
For every admissible valuation of x0, P holds.
```

The language-level meaning of:

```forml
exists x0 with domain(...) => P
```

is:

```text
There exists at least one admissible valuation of x0 for which P holds.
```

Universal proof by refutation and existential witness search are different verification semantics. A backend or runner must not treat them as interchangeable.

### Initial scope

The initial language supports one explicitly named variable per quantified property.

Multiple-variable quantification, nested quantifiers, and shadowing are deferred. Their future introduction must preserve the same exact-binding rule.

## Rationale

Explicit quantified bindings make the property self-contained and readable.

They also provide a stable semantic contract:

```text
source identifier
→ CST identifier
→ AST quantified variable
→ SymbolTable entry
→ SemanticContext variable
→ ScopeIR variable
→ backend symbol
```

Rejecting alias fallback for explicit entities prevents typographical errors from changing meaning silently. At the same time, keeping implicit assertion references preserves a concise user-facing syntax when the scope has an unambiguous default entity.

## Consequences

### Positive

- Quantified variables are visible in the DSL.
- Domain and assertion references can be checked against the same binding.
- Diagnostics can report the exact undeclared identifier.
- IR and backend variables remain traceable to source syntax.
- Future multi-variable scopes have a sound binding foundation.
- `target` remains clearly separated from input features.

### Negative

- Existing implicit forms such as `forall => ...` or `forall with ... => ...` become invalid unless a compatibility migration is introduced.
- Parser, AST, semantic context, IR scope, tests, and documentation must all be updated together.
- The semantic validator must distinguish implicit feature shorthand from invalid explicit entities.
- Existential execution requires dedicated backend semantics and cannot reuse universal refutation mechanically.

## Alternatives considered

### Keep an implicit `_x` variable

Rejected because it hides the quantified symbol, complicates explicit feature qualification, and makes future multi-variable properties awkward.

### Allow either explicit or omitted identifiers permanently

Rejected as the normative design because it creates two public forms for the same concept and keeps the implicit-binding ambiguity alive. A temporary migration path may be considered separately, but it is not part of the target language contract.

### Alias any unknown explicit entity to the only variable in scope

Rejected because a typo such as `x1.age` inside `forall x0` would be accepted with altered meaning.

### Require explicit qualification everywhere

Rejected for assertions because concise expressions such as `age >= 18` are useful when the scope supplies one unambiguous default entity. Domain subjects remain explicitly qualified because they are declaration-like constraints and must be future-proof for multi-variable scopes.

## Impact on FORML

### Grammar

Quantifier expressions require an identifier:

```text
quantifier_expr = quantifier , identifier , [ domain ] ;
```

### AST

The quantified scope node stores the declared identifier explicitly.

### Semantic validation

The LHS validator registers the identifier and establishes it as the default entity. Binding validation rejects unknown explicit entities instead of applying a single-variable alias fallback.

### IR

`ScopeIR.variables` preserves the declared symbol and its `symbolic` role. Generated backend symbols must remain traceable to this identifier.

### Tests

Required tests include:

- valid `forall x0` and `exists x0` parsing;
- missing identifier rejection;
- implicit feature resolution to the quantified identifier;
- exact explicit-entity binding;
- explicit entity mismatch rejection;
- domain subject mismatch rejection;
- target-only quantified assertions;
- separation of universal and existential verification semantics.

### Related documentation

- `language/quantified-bindings.md`
- `language/scopes.md`
- `language/domains.md`
- `contracts/ast-to-semantic.md`
- `contracts/semantic-to-ir1.md`
