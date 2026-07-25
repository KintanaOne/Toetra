# Parser Layer

> Status: P0 / Implemented  
> Scope: Source to CST  
> Implementation: Lark-based parser  
> Audience: compiler contributors, grammar maintainers, test authors

## Purpose

The parser layer converts raw `.toetra` source code into a Concrete Syntax Tree.

It answers the question:

```text
Is this text syntactically valid Toetra?
```

The parser does not interpret semantic meaning. It only recognizes whether the source conforms to the grammar.

---

## Input and Output

```text
Input:  raw `.toetra` source string
Output: CST / Lark Tree
```

The CST preserves syntax-level structure and grammar shape.

---

## Responsibilities

The parser layer is responsible for:

- loading the Toetra grammar;
- configuring the parser;
- parsing raw text;
- producing a CST;
- rejecting syntactically invalid programs;
- preserving enough tree structure for the builder layer.

---

## Current Implementation

The current parser is based on Lark.

Conceptually:

```python
toetra_parser = Lark(
    grammar,
    start="program",
    parser="lalr",
    propagate_positions=True,
    maybe_placeholders=True,
)

cst = toetra_parser.parse(source)
```

The parser currently targets the `program` grammar rule.

---

## Parser Contract

The parser contract is:

```text
Valid Toetra source
    → CST

Invalid syntax
    → Parser error
```

The parser must not return partial AST objects or semantic artifacts.

---

## CST Characteristics

A CST is expected to preserve:

- source-level grammar structure;
- rule names;
- tokens;
- nesting;
- property section boundaries;
- header declarations;
- assertion structure;
- backend declarations.

A CST may contain grammar-specific noise. Removing or interpreting that noise is the responsibility of the builder layer.

---

## Guarantees

The parser layer guarantees:

- syntactically invalid source is rejected;
- syntactically valid source produces a tree;
- the output is grammar-driven, not semantically interpreted;
- no AST node is constructed at this layer;
- no model information is loaded or inspected.

---

## Non-Goals

The parser must not:

- resolve variables;
- infer implicit entities;
- validate property-scope compatibility;
- validate feature existence;
- normalize logical formulas;
- select backends;
- call ModelBridge;
- call Miova.

---

## Error Boundary

Parser errors should represent source syntax errors only.

Examples:

| Error | Parser Concern? |
|---|---:|
| Missing bracket in property declaration | Yes |
| Invalid grammar structure | Yes |
| Unknown variable in assertion | No |
| Unsupported model format | No |
| Property incompatible with scope | No |

Semantic errors must not be collapsed into parser errors in the final stabilized architecture.

---

## Stabilization Requirements

| Requirement | Reason |
|---|---|
| Remove runtime dependency on test fixtures | Production parser should not import test samples. |
| Resolve grammar path robustly | Parser should work independently of current working directory. |
| Define parser cache policy | Dev and production may use different settings. |
| Preserve source positions | Better diagnostics and mutation reporting. |
| Map raw parser errors into Toetra-specific parser errors | Cleaner user feedback. |

---

## Relation to Builder

The builder consumes the CST and produces a Toetra AST.

The parser must not hide information that the builder needs.

The builder must not rely on fragile positional assumptions if a stable tree navigation strategy can be used.

---

## Relation to Miova

Miova may generate malformed or mutated source programs to validate parser behavior.

Expected outcomes include:

- accepted valid variants;
- rejected invalid syntax;
- stable parser diagnostics;
- no crashes outside the parser error boundary;
- no semantic error produced before syntax is valid.
