# Builder Layer

> Status: P0 / Implemented / Stabilizing  
> Scope: CST to AST  
> Implementation: custom CST traversal and AST construction  
> Audience: compiler contributors, AST maintainers, test authors

## Purpose

The builder layer converts the Concrete Syntax Tree into Toetra AST nodes.

It answers the question:

```text
What structured Toetra program does this syntactic tree represent?
```

The builder is the first layer that turns grammar-specific structures into domain-specific compiler artifacts.

---

## Input and Output

```text
Input:  CST / Lark Tree
Output: ProgramNode / AST
```

The output must no longer expose raw Lark structures.

---

## Responsibilities

The builder layer is responsible for:

- extracting header declarations;
- extracting property sections;
- detecting property scope type;
- building expression nodes;
- building assertion nodes;
- parsing comparison operators;
- parsing constants;
- parsing backend hints;
- constructing a `ProgramNode`.

---

## Main Builder Products

The builder produces a tree of Toetra AST nodes, including:

| AST Node | Meaning |
|---|---|
| `ProgramNode` | Full Toetra program. |
| `HeaderNode` | Model and target declarations. |
| `PropertyNode` | One property section. |
| `PropertyRuleNode` | Scope + assertion. |
| `ExpressionNode` variants | LHS evaluation context. |
| `AssertionNode` | RHS logical assertion wrapper. |
| `LogicalNode` variants | Boolean and predicate structure. |
| `BackendNode` | Optional backend hint. |

---

## Builder Pipeline

```text
CST
    ↓
parse_program
    ↓
parse_header
    ↓
parse_property sections
    ↓
parse scope
    ↓
parse assertion
    ↓
parse backend
    ↓
ProgramNode
```

---

## Builder Guarantees

The builder must guarantee:

- no raw Lark tree leaks into the AST;
- required AST fields are present;
- missing mandatory syntax is rejected;
- primitive constants are typed;
- property scopes are represented by explicit node classes;
- assertion structure is represented by explicit logical nodes;
- backend hints are captured without backend execution.

---

## Strict Boundary

The builder may enforce structural validity, but not semantic validity.

Examples:

| Check | Builder? | Later Layer? |
|---|---:|---:|
| Missing RHS assertion | Yes | No |
| Unknown scope grammar shape | Yes | No |
| Unknown variable `x` | No | Semantic |
| `ROBUSTNESS` used with invalid scope | No | Semantic |
| Feature not present in model schema | No | Schema/Semantic integration |
| `NOT` normalization | No | IR1 |

---

## Attribute Handling

The builder parses attributes into structured nodes.

Examples:

| Source | Parsed Entity | Parsed Feature | Path |
|---|---|---|---|
| `age` | `None` | `age` | `['age']` |
| `x.age` | `x` | `age` | `['x', 'age']` |
| `x.profile.age` | `x` | `age` | `['x', 'profile', 'age']` |

The builder does not resolve implicit entities. It only preserves parsed structure.

Implicit resolution belongs to semantic binding.

---

## Assertion Handling

The builder turns assertion syntax into logical nodes.

Examples:

| Source Construct | AST Node |
|---|---|
| `a <= 1` | `ComparisonNode` |
| `A AND B` | `AndNode` |
| `A OR B` | `OrNode` |
| `NOT A` | `NotNode` |
| `A -> B` | `ImplicationNode` |
| `CLASSIFICATION.EQUAL()` | `ProblemNode` |

The builder should preserve logical structure but should not rewrite it.

---

## Stabilization Requirements

| Topic | Required Action |
|---|---|
| Header parsing | Ensure `parse_header` works consistently whether called on program or header subtree. |
| Logic expression handling | Clarify whether `logic_expr` is still part of the grammar or should be removed. |
| Backend args | Normalize backend argument parsing and value typing. |
| Enum conversion | Centralize enum parsing to avoid inconsistent value/name handling. |
| Pairwise parsing | Preserve `x ~ x'` syntax for semantic and IR layers. |
| Quantifier parsing | Normalize unicode and word quantifiers. |

---

## Building Specification Constants and Bare Names

The builder:

- creates one `SpecificationConstantDeclarationNode` per header declaration;
- stores declarations on `HeaderNode` in source order;
- builds typed `ConstantNode` values for declaration literals;
- builds `NameRefNode` for bare scalar identifiers;
- preserves explicit qualified features as `AttributeNode`;
- does not perform constant lookup or implicit-feature fallback.

The following two expressions must remain structurally distinguishable:

```toetra
threshold
x0.threshold
```

The first becomes `NameRefNode("threshold")`; the second becomes an explicit feature reference.

## Relation to Semantic Layer

The semantic layer consumes the AST produced by the builder.

The builder must preserve enough information for semantic validation:

- property type;
- scope node;
- assertion root;
- raw attribute entity and feature;
- backend hint;
- domains;
- neighborhoods;
- constants and primitive types.

---

## Relation to Miova

Miova can mutate AST artifacts after the builder layer.

Example AST mutations:

- remove assertion root;
- replace comparison operator;
- corrupt property type;
- remove neighborhood epsilon;
- change scope type;
- corrupt backend hint;
- replace explicit entity with unknown entity.

Expected outcomes should be defined by AST and semantic contracts.
