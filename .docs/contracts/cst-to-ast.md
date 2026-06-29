# CST to AST Contract

> Status: P0 / Implemented / Stabilizing  
> Scope: Concrete Syntax Tree to FORML AST  
> Implementation: custom builder layer  
> Audience: builder maintainers, AST maintainers, Miova campaign authors

## Purpose

The CST to AST contract defines how parser-specific structures become FORML domain objects.

It answers the question:

```text
What structured FORML program does this syntax tree represent?
```

The builder removes grammar noise and produces typed domain nodes.

---

## Input

```text
CST: Lark Tree
```

Preconditions:

- CST was produced by the official FORML parser;
- CST root corresponds to a complete program;
- no semantic validation is assumed.

---

## Output

```text
ProgramNode
```

The AST root must contain:

- `HeaderNode`;
- one or more `PropertyNode` objects;
- each property with a `PropertyRuleNode`;
- each rule with a scope expression and assertion;
- optional backend metadata.

---

## Main AST Products

| Node | Purpose |
|---|---|
| `ProgramNode` | Full FORML program. |
| `HeaderNode` | Model and target declarations. |
| `PropertyNode` | One property section. |
| `PropertyRuleNode` | LHS scope + RHS assertion. |
| `ExpressionNode` variants | `at`, `check_at`, `pairwise`, quantifier contexts. |
| `AssertionNode` | RHS wrapper. |
| `LogicalNode` variants | Boolean and predicate structure. |
| `BackendNode` | Optional backend hint. |

---

## Guarantees

If the builder succeeds:

- no raw Lark nodes should be required by downstream layers;
- AST nodes should represent FORML concepts directly;
- mandatory syntactic information should be present;
- optional constructs should be represented explicitly as `None` or empty collections;
- AST construction should fail early on structurally invalid CST shapes.

---

## Non-Goals

The builder must not:

- resolve variable bindings;
- infer implicit entities;
- validate property/scope compatibility;
- validate feature existence in a model;
- normalize logical expressions into NNF/CNF/DNF;
- generate backend queries.

---

## Failure Modes

The builder should reject:

- missing model declaration;
- missing target declaration;
- unsupported property mode;
- missing RHS assertion;
- invalid comparison structure;
- invalid backend argument structure;
- malformed domain or neighborhood nodes.

---

## Stabilization Notes

Current builder stabilization should focus on:

- consistent enum normalization;
- consistent quantifier normalization;
- strict AST node inheritance policy;
- robust pairwise parsing;
- avoiding accidental runtime dependency on test fixtures;
- ensuring `logic_expr` grammar nodes are either supported or removed.

---

## Miova Hooks

Miova may mutate CST or AST-adjacent artifacts by:

- removing required subtrees;
- swapping property modes;
- corrupting backend nodes;
- replacing comparison operators;
- replacing assertion nodes;
- generating syntactically valid but structurally unexpected CST shapes.

Expected outcomes:

| Mutation | Expected Boundary |
|---|---|
| CST shape invalid | Builder rejection. |
| AST structurally valid but semantically invalid | Semantic rejection later. |
| AST still valid | Continue to semantic validation. |
