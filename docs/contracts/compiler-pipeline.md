# Compiler Pipeline Contract

> Status: P0 / Stabilizing with accepted target extensions  
> Scope: End-to-end compiler artifact progression  
> Audience: compiler maintainers, architecture maintainers and Miova campaign authors

## Purpose

This contract defines the official progression of Toetra artifacts and prohibits cross-layer shortcuts.

---

## Official Artifact Chain

```text
SourceText
→ CST
→ ProgramNode AST
→ SemanticValidatedAST
→ VerificationTask IR1
→ VerificationTask IR2
→ Aggregated verification condition
→ BackendQuery
→ VerificationResult
```

The model path contributes:

```text
ModelArtifact
→ ModelSchema
→ ModelAssumptions
→ VerificationTask IR2 / aggregation
```

---

## Artifact Ownership

| Artifact | Producer | May contain | Must not contain |
|---|---|---|---|
| SourceText | User/tooling | Public DSL syntax | Compiler objects |
| CST | Parser | Grammar structure and tokens | Resolved symbols, solver objects |
| AST | Builder | Typed syntax nodes | Assumed binding, Z3 expressions |
| SemanticValidatedAST | Semantic passes | Resolved symbols, types, context | Backend expressions |
| IR1 | IR1 translator | Backend-independent scopes, scalar/logical expressions, typed domains | Lark nodes, unresolved references |
| IR2 | IR2 builder/normalizer | Normal forms, assumptions, requirements, verification semantics | Raw DSL syntax |
| BackendQuery | Backend compiler | Backend-native declarations and formulas | Unchecked requirements |

---

## New Language Feature Flow

### Quantified identifier

```text
forall x0
```

must progress as:

```text
identifier token
→ AST scope variable `x0`
→ semantic symbol `x0`
→ IR scope variable `x0`
→ backend-symbol provenance `x0`
```

### Typed domain

```text
Domain syntax
→ typed Domain AST
→ validated typed domain
→ typed Domain IR1
→ DOMAIN assumptions in IR2
→ backend expressions
```

### Scalar comparison

```text
source arithmetic tree
→ scalar AST tree
→ resolved/typed scalar tree
→ scalar IR1 tree
→ comparison atom in IR2
→ recursive backend scalar encoding
```

---

## Global Guarantees

The pipeline must guarantee:

1. each layer consumes only its declared input artifact;
2. each transformation either produces a valid next artifact or fails explicitly;
3. source identifiers and provenance remain traceable;
4. no solver object leaks before the backend boundary;
5. no unresolved input or target reference enters IR1;
6. domain assumptions remain distinct from the property formula;
7. requirement analysis precedes backend compilation;
8. unsupported expressions are rejected, not approximated;
9. universal and existential semantics are preserved through result interpretation.

---

## Verification-Condition Branch

A quantified task does not become a native solver quantifier automatically.

The initial semantics use symbolic variables and different verification conditions.

Universal:

```text
Γdomain ∧ Γmodel ∧ ¬P
```

Existential:

```text
Γdomain ∧ Γmodel ∧ P
```

Native backend quantifiers are a separate future capability.

---

## Expected Failure Boundaries

| Failure | Boundary |
|---|---|
| Malformed quantified syntax | Source → CST |
| Malformed expression/domain CST | CST → AST |
| Unbound or mismatched entity | AST → Semantic |
| Type-invalid arithmetic/domain | AST → Semantic |
| Missing semantic resolution | Semantic → IR1 |
| Invalid normal form or provenance | IR1 → IR2 |
| Invalid condition composition | Aggregation |
| Unsupported required capability | Routing / IR → Backend |
| Solver runtime failure | Backend runtime |

---

## Forbidden Shortcuts

The following paths are invalid:

```text
Source → Z3
AST → Z3
Raw Domain AST → Z3
Unvalidated scalar AST → IR2
Backend capability repair inside the parser
```

Compatibility adapters may exist temporarily, but they must not redefine the target contract.

## Specification Constant Pipeline Invariant

Across the full compiler pipeline:

```text
header declaration
→ typed declaration AST
→ registered semantic symbol
→ resolved bare-name occurrence
→ typed constant IR with provenance
→ backend literal
```

No stage may silently reinterpret a specification constant as a model feature or unconstrained backend variable.
