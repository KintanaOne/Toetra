# AST Layer

> Status: P0 / Implemented / Stabilizing  
> Scope: FORML domain syntax representation  
> Implementation: dataclass-based AST nodes  
> Audience: compiler contributors, semantic validators, Miova mutation authors

## Purpose

The AST layer represents a FORML program as structured domain objects.

It answers the question:

```text
What is the syntactic structure of the FORML program, independent of parser details?
```

The AST is not the semantic truth of the program. It is the typed syntactic representation consumed by semantic validation.

---

## AST Position in the Pipeline

```text
CST
    ↓
Builder
    ↓
AST
    ↓
Semantic Validation
    ↓
SemanticValidatedAST
```

The AST sits between parser-specific syntax and semantic interpretation.

---

## Main AST Families

| Family | Examples | Responsibility |
|---|---|---|
| Program nodes | `ProgramNode`, `HeaderNode` | Whole program structure. |
| Property nodes | `PropertyNode`, `PropertyRuleNode` | Property declaration and rule. |
| Expression nodes | `AtExprNode`, `PairwiseExprNode`, `CheckAtExprNode`, `QuantifierExprNode` | LHS evaluation context. |
| Assertion nodes | `AssertionNode`, `ComparisonNode`, `AndNode`, `OrNode`, `NotNode`, `ImplicationNode`, `ProblemNode` | RHS logical intent. |
| Primitive nodes | `AttributeNode`, `ConstantNode`, `ArgNode` | Leaves and values. |
| Backend nodes | `BackendNode` | Optional backend hint. |
| Domain/neighborhood nodes | `DomainNode`, `NeighborhoodNode` | Scope modifiers. |

---

## AST Design Intent

The AST must be:

- parser-independent;
- explicit;
- typed enough for semantic validation;
- mutable only where semantic enrichment is required;
- stable enough to serve as a Miova mutation target;
- free from backend-specific solver objects.

---

## AST vs SemanticValidatedAST

The AST is the builder output.

The `SemanticValidatedAST` is not necessarily a separate Python class today. It is the AST after semantic validation has attached or populated semantic metadata.

Conceptually:

```text
AST
    + SemanticContext
    + SymbolTable
    + resolved attributes
    + compatibility validation
    = SemanticValidatedAST
```

This distinction matters for documentation and testing.

---

## Semantic Annotations

Some AST nodes can be enriched with semantic annotations after validation.

Semantic annotations may include:

- semantic context;
- symbol table;
- logical root;
- resolved entity;
- resolved path;
- resolved type;
- resolved symbol;
- constraints.

The AST must not depend on semantic annotations before the semantic layer runs.

---

## AST Invariants

The following invariants should hold for any builder-produced AST:

| Invariant | Description |
|---|---|
| Program has a header | Every `ProgramNode` has a `HeaderNode`. |
| Program has body | A valid program contains one or more properties. |
| Property has a rule | Every property has a scope and assertion. |
| Scope is explicit | Scope is one of the supported expression node types. |
| Assertion has root | Every assertion wraps a logical root. |
| Comparison has operands | Comparisons have left attribute, operator and right constant. |
| Backend hint is optional | Absence of backend does not invalidate AST. |

---

## Non-Goals

The AST layer must not:

- validate semantic scope compatibility;
- infer implicit entities;
- check model feature existence;
- perform NNF or CNF/DNF rewriting;
- select a verification backend;
- encode solver formulas.

---

## Stabilization Requirements

| Topic | Required Decision |
|---|---|
| Common base class | Decide whether all AST nodes, including `ProgramNode`, `HeaderNode`, `PropertyNode`, and primitives, should inherit a common `ASTNode`. |
| Semantic field policy | Decide whether every semantic-capable node explicitly declares `semantic`. |
| Immutability | Decide whether AST nodes remain mutable or semantic validation returns a separate enriched tree. |
| Source spans | Decide whether AST nodes carry source position metadata. |
| Error reporting | Define how AST nodes participate in diagnostics. |

---

## Relation to IR

IR must not copy raw AST assumptions blindly.

IR should consume semantic information when available, especially for resolved attributes.

Example:

```text
Raw AST attribute: age
Semantic resolution: x'.age
IR comparison: entity = x', feature = age
```

This prevents implicit DSL syntax from becoming ambiguous in backend-facing representations.

---

## Relation to Miova

The AST is one of the most important Miova mutation boundaries.

Miova can use AST mutations to test:

- semantic validator robustness;
- IR translator assumptions;
- enum normalization;
- missing field handling;
- invalid scope/property combinations;
- logical edge cases.

The AST contract should define which mutations are expected to be rejected and at which layer.
