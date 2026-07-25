# C4 Component View — DSL Compiler

> Status: Stabilizing  
> Scope: Compiler component architecture  
> Implementation: Implemented until IR1 / planned after IR1  
> V1 backend scope: Z3 only

## Purpose

This document decomposes the Toetra Specification Language Compiler into internal components.

It answers:

```text
How does FORML transform `.toetra` source into semantically valid IR?
```

---

## Component diagram

```mermaid
flowchart TD
    Source[.toetra Source]
        --> Grammar[Language Grammar]

    Grammar
        --> Parser[Lark Parser]

    Parser
        --> CST[CST]

    CST
        --> Builder[AST Builder]

    Builder
        --> AST[AST]

    AST
        --> Constants[Specification Constant Collector]

    Constants
        --> ProgramSymbols[Program Symbol Table]

    AST
        --> LHS[LHS Validator]

    LHS
        --> Context[SemanticContext]

    Context
        --> Binding[Binding / Name Resolver]

    ProgramSymbols
        --> Binding

    Binding
        --> Logic[Logic Validator]

    Logic
        --> Property[Property Validator]

    Property
        --> SemanticAST[SemanticValidatedAST]

    SemanticAST
        --> IR1[IR1 Translator]
```

---

## Components

| Component | Responsibility | Output | Status |
|---|---|---|---|
| Language Grammar | Defines legal Toetra syntax. | Grammar rules | Implemented / stabilizing |
| Lark Parser | Parses source text. | CST | Implemented |
| AST Builder | Converts CST into typed AST nodes, including declaration and bare-name nodes. | AST | Implemented / target evolution pending |
| Specification Constant Collector | Registers immutable program-level declarations. | Program symbol table | Accepted target / implementation pending |
| LHS Validator | Builds semantic scope and variables. | SemanticContext | Implemented / stabilizing |
| Binding / Name Resolver | Resolves constants, explicit features and implicit features by context. | Semantic annotations | Implemented foundation / target evolution pending |
| Logic Validator | Validates logical structure and problem/function compatibility. | Validated logic | Implemented / needs fixes |
| Property Validator | Orchestrates semantic validation for one property. | SemanticValidatedAST | Implemented / stabilizing |
| IR1 Translator | Translates validated AST into IR1 tasks. | VerificationTask list | Implemented / stabilizing |

---

## Compiler artifact flow

```text
Source
→ CST
→ AST
→ Program-level specification constant symbols
→ SemanticContext
→ SemanticAnnotations
→ SemanticValidatedAST
→ IR1 VerificationTask
```

The compiler should never skip a layer. Each layer has a contract and expected failure modes.

---

## Language Grammar

The language grammar defines:

- headers;
- model and target declarations;
- specification-constant declarations;
- property sections;
- scopes;
- assertions;
- comparison operators;
- backend syntax.

The grammar is not responsible for semantic validity. It only defines what can be parsed.

---

## Parser

The parser converts raw `.toetra` source into a concrete syntax tree.

Responsibilities:

- preserve syntax structure;
- expose parse errors;
- avoid semantic interpretation;
- provide a stable input for the builder.

---

## AST Builder

The builder converts the CST into typed Python nodes.

Responsibilities:

- remove syntactic noise;
- build `ProgramNode`, `HeaderNode`, specification-constant declarations, properties, scopes and assertions;
- preserve bare names without semantic guessing;
- preserve explicit user intent;
- reject structurally invalid CST fragments.

---

## Semantic validation

Semantic validation is composed of several passes.

| Pass | Purpose |
|---|---|
| Specification constant registration | Builds the global immutable declaration table before property validation. |
| LHS validation | Defines scope, variables, default entity, domain and neighborhood. |
| Binding/name resolution | Resolves constants, explicit features and implicit features according to context. |
| Logic validation | Validates logical operators, comparisons, and problem-level predicates. |
| Property compatibility | Ensures property type supports the selected semantic scope. |

The output of semantic validation is not a new syntax tree type yet; it is the AST enriched with semantic annotations and validated context.

---

## Specification Constant Components

The compiler includes two additional conceptual responsibilities:

| Component | Responsibility | Status |
|---|---|---|
| Specification Constant Collector | Build the program-level table of immutable declarations. | Accepted target / implementation pending |
| Name Resolver | Resolve `NameRefNode` by context without guessing in the builder. | Accepted target / implementation pending |

Target flow:

```text
Header declarations
    → SpecificationConstantDeclarationNode list
    → program-level constant symbols

Property scalar expressions
    → NameRefNode
    → context-aware semantic resolution
    → constant reference or implicit feature
```

The builder preserves ambiguity; the semantic layer owns lookup and collision diagnostics.

## IR1 translation

IR1 translation turns semantic AST nodes into backend-independent verification tasks.

The translator should consume resolved semantic information, not raw unresolved syntax.

Target invariant:

```text
IR1 must not contain unresolved attributes.
```

---

## Implementation status

| Area | Status | Notes |
|---|---|---|
| Grammar | Implemented / stabilizing | Operator casing and quantifier normalization need cleanup. |
| Parser | Implemented | Uses Lark. |
| Builder | Implemented / stabilizing | AST node inheritance/semantic fields should be normalized. |
| Semantic validation | Implemented / needs fixes | Enum normalization and error boundaries need stabilization. |
| IR1 translation | Implemented / needs fixes | Should use semantic annotations for resolved entities. |
| IR2 translation | Planned | Covered by logical pipeline docs. |
| Backend lowering | Planned | Z3-first. |

---

## Related contracts

- `contracts/source-to-cst.md`
- `contracts/cst-to-ast.md`
- `contracts/ast-contract.md`
- `contracts/ast-to-semantic.md`
- `contracts/semantic-to-ir1.md`
- `contracts/errors.md`
- `contracts/type-normalization.md`
- `contracts/specification-constants.md`
