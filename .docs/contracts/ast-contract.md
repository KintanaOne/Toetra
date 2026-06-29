# AST Contract

> Status: P0 / Implemented / Stabilizing  
> Scope: FORML domain syntax representation  
> Implementation: dataclass-based nodes  
> Audience: AST maintainers, semantic validators, Miova mutation authors

## Purpose

The AST contract defines what a valid FORML AST is before semantic validation.

It answers the question:

```text
What shape must the FORML program have before meaning is checked?
```

The AST is the domain-level syntax representation of a `.forml` program.

---

## AST Root

The AST root is:

```text
ProgramNode
```

A valid `ProgramNode` contains:

- `header: HeaderNode`;
- `body: list[PropertyNode]`.

The body must contain at least one property before meaningful verification can occur.

---

## Required Families

| Family | Required Nodes |
|---|---|
| Program | `ProgramNode`, `HeaderNode` |
| Property | `PropertyNode`, `PropertyRuleNode` |
| Scope | `AtExprNode`, `CheckAtExprNode`, `PairwiseExprNode`, `QuantifierExprNode` |
| Assertion | `AssertionNode`, `ComparisonNode`, `AndNode`, `OrNode`, `NotNode`, `ImplicationNode`, `ProblemNode` |
| Primitive | `AttributeNode`, `ConstantNode`, `ArgNode` |
| Context | `DomainNode`, `NeighborhoodNode`, `BackendNode` |

---

## AST Guarantees

A valid AST must guarantee:

- no raw Lark tree is required downstream;
- each property has exactly one scope expression;
- each property has one assertion root;
- attributes preserve raw parsed path information;
- constants preserve parsed value and inferred dtype;
- backend hints are optional;
- domain and neighborhood modifiers are explicit when present.

---

## Semantic Attachment Policy

The AST contract distinguishes two states:

```text
AST
SemanticValidatedAST
```

Today, `SemanticValidatedAST` is represented by the AST after semantic annotations have been attached to relevant nodes.

The target contract should decide whether:

- all AST nodes inherit a semantic-capable base class; or
- only specific nodes expose semantic metadata explicitly.

The contract requires this policy to be explicit and stable.

---

## Non-Goals

The AST must not:

- encode solver-specific details;
- decide backend compatibility;
- perform NNF/CNF/DNF rewriting;
- represent model internals;
- aggregate constraints;
- perform minimization.

---

## Invariants

| Invariant | Description |
|---|---|
| Parser independence | AST users should not depend on Lark. |
| Domain explicitness | FORML concepts are represented as FORML nodes. |
| No backend leakage | AST contains backend hints only, not backend queries. |
| No semantic assumption | Raw AST may contain unresolved variables. |
| Stable mutation target | Miova can mutate AST nodes without parser involvement. |

---

## Miova Hooks

Miova may mutate AST by:

- removing required property fields;
- replacing a scope type;
- corrupting an attribute path;
- changing constant dtype;
- replacing a logical node;
- deleting backend hints;
- injecting unknown logical nodes.

Expected outcome depends on mutation severity:

| Mutation Type | Expected Outcome |
|---|---|
| Structural invalidity | AST or semantic rejection. |
| Semantic invalidity | Semantic rejection. |
| Valid alternative structure | Continue to semantic validation. |
