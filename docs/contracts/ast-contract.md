# AST Contract

> Status: Implemented and accepted structure
> Scope: Raw typed Toetra syntax before semantic validation
> Audience: AST maintainers, semantic validators and mutation authors

## Purpose

The AST answers:

```text
What structured syntax did the user write?
```

It does not yet guarantee that the syntax has valid meaning for a scope or model.

---

## Required Node Families

| Family | Conceptual nodes |
|---|---|
| Program | `ProgramNode`, `HeaderNode` |
| Property | `PropertyNode`, `PropertyRuleNode` |
| Scope | `CheckAtExprNode`, `AtExprNode`, `PairwiseExprNode`, `QuantifierExprNode` |
| Boolean | `AssertionNode`, `ComparisonNode`, `AndNode`, `OrNode`, `NotNode`, `ImplicationNode`, `ProblemNode` |
| Scalar | `ScalarExpressionNode`, `ConstantNode`, `AttributeNode`, `TargetRefNode`, `UnaryArithmeticNode`, `BinaryArithmeticNode` |
| Domain | `DomainNode`, `DomainEntryNode`, `IntervalDomainNode`, `FiniteSetDomainNode`, boundary-kind and literal-kind vocabulary |
| Other context | `NeighborhoodNode`, `BackendNode`, `ArgNode` |

Concrete Python names may differ, but the represented concepts and invariants are normative.

---

## Quantified Scope Invariants

A raw quantified-scope node contains:

```text
quantifier: canonical quantifier kind
variable: non-empty source identifier
domain: typed domain or None
```

Raw AST guarantees identity preservation, not binding correctness.

The AST must not replace the source variable with `_x` or another internal alias.

---

## Scalar Expression Invariants

- leaves are constants, attributes or target references;
- unary nodes contain exactly one operand;
- binary nodes contain exactly two ordered operands;
- comparisons contain exactly two scalar expressions;
- chained comparisons are absent;
- source grouping is represented by tree shape;
- no backend-native arithmetic object is present.

Raw AST may still contain:

- an unknown explicit entity;
- arithmetic over incompatible types;
- unsupported nonlinear structure;
- a literal zero denominator.

Those are semantic or capability concerns.

---

## Domain Invariants

A raw domain AST satisfies structural rules:

- the domain contains at least one entry;
- every subject is an explicitly qualified attribute syntax node;
- every entry contains exactly one interval or finite-set constraint;
- interval lower/upper expressions and boundary kinds are preserved;
- finite sets contain at least one typed member;
- symbolic category literals are distinct from strings and feature references;
- source provenance is available when parser position data exists.

Raw AST does not guarantee:

- subject binding to the scope variable;
- unique subject features;
- interval non-emptiness;
- set-member compatibility;
- numeric bound types;
- backend encodability.

---

## Target Reference Invariant

`TargetRefNode` represents the model output declared in the header.

It is distinct from:

```text
AttributeNode(entity="target", ...)
```

The target reference may appear in assertions and assertion arithmetic, but a later semantic rule rejects it in input-domain subjects or bounds.

---

## Semantic Attachment Boundary

The raw AST and SemanticValidatedAST are distinct artifacts.

Semantic annotations may be attached to AST nodes as the current representation strategy, but downstream code must not infer semantic validity merely from node type.

A validated marker/context or successful semantic pass is required.

---

## Forbidden AST Content

The AST must not contain:

- Lark nodes required for interpretation;
- Z3 expressions;
- backend variable declarations;
- model coefficients as implicit syntax;
- expanded domain boolean formulas;
- guessed entity bindings;
- silent arithmetic approximations.

## Specification Constant Invariants

The target AST satisfies:

- `HeaderNode` preserves all specification-constant declarations;
- declaration values are typed literal nodes;
- bare scalar names use `NameRefNode` until semantic resolution;
- explicit qualified features remain structurally distinct;
- `target` remains a dedicated output reference;
- no declaration is represented as a backend variable;
- no implicit-feature guess is stored in raw AST.
