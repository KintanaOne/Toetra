# Source to CST Contract

> Status: P0 / Implemented  
> Scope: Raw FORML source to Concrete Syntax Tree  
> Implementation: Lark parser  
> Audience: parser maintainers, grammar authors, test authors

## Purpose

The Source to CST contract defines the parser boundary.

It answers the question:

```text
When is raw text syntactically valid FORML?
```

This layer is purely syntactic. It does not validate semantic meaning.

---

## Input

```text
SourceText: str
```

The input is a raw `.forml` source string.

It may contain:

- header declarations;
- property sections;
- scope expressions;
- logical assertions;
- backend hints;
- comments and whitespace.

---

## Output

```text
CST: Lark Tree
```

The CST must:

- be rooted at the `program` grammar rule;
- preserve grammar structure;
- expose enough structure for AST construction;
- remain free from FORML semantic annotations;
- remain free from backend objects.

---

## Guarantees

If parsing succeeds:

- the source conforms to the grammar;
- the output is a CST, not an AST;
- the parser did not perform semantic validation;
- the parser did not infer model information;
- no type compatibility has been checked yet.

---

## Non-Goals

The parser must not:

- resolve variables;
- infer default entities;
- check property/scope compatibility;
- validate model features;
- produce IR;
- normalize boolean logic;
- choose a backend.

---

## Failure Modes

The parser should reject:

- malformed property declarations;
- invalid header syntax;
- invalid expression structure;
- unsupported tokens;
- invalid nesting or missing separators.

The error should remain in the parsing family and not be confused with semantic errors.

---

## Stabilization Notes

The parser currently uses a Lark grammar loaded from a grammar file.

The contract should eventually require:

- stable grammar file path resolution;
- no dependency on test fixtures in runtime parser code;
- consistent casing for logical operators;
- strict separation between generated grammar and vocabulary definitions;
- parser tests for all official examples.

---

## Miova Hooks

Miova may mutate source text by:

- deleting delimiters;
- corrupting keywords;
- changing logical operators;
- changing property names;
- changing backend syntax;
- injecting malformed scopes.

Expected outcomes:

| Mutation | Expected Status |
|---|---|
| Still syntactically valid | CST produced, downstream layer decides. |
| Syntactically invalid | Parser rejection. |
| Semantically invalid but syntactically valid | CST produced; semantic layer rejects later. |
