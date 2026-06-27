# `architecture/ast/expression_model.md`

# Expression Model

## 1. Purpose

Define structured expression representations used inside assertions.

---

## 2. Responsibilities

Expressions represent:

- data references,
- attribute access,
- constants,
- symbolic references.

---

## 3. Expression Categories

- AttributeNode
- ConstantNode
- FeatureReferenceNode
- VariableReferenceNode

---

## 4. Expression Characteristics

Expressions are:

- backend-agnostic,
- structurally normalized,
- deterministic.

---

## 5. Invariants

- Expression hierarchy remains valid.
- Feature access remains normalized.
- Expression structures remain deterministic.