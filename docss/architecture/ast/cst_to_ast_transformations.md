# `architecture/ast/cst_to_ast_transformations.md`

# CST to AST Transformations

## 1. Purpose

Define structural transformations applied during AST construction.

---

## 2. Transformation Overview

```mermaid
flowchart LR

    A[CST]
        --> B[Node Mapping]

    B --> C[Scope Extraction]
    B --> D[Expression Mapping]
    B --> E[Logical Restructuring]

    C --> F[AST]
    D --> F
    E --> F
````

---

## 3. Transformation Stages

## Node Mapping

Examples:

* grammar expressions → AST expressions
* syntax operators → logical nodes
* comparisons → ComparisonNode

---

## Scope Extraction

Examples:

* `at x` → LocalScope
* `forall x` → QuantifierScope

---

## Expression Normalization

Examples:

* flattened attribute access,
* normalized feature references,
* deterministic expression representation.

---

## Logical Structuring

Examples:

* implication normalization,
* unary operator normalization,
* logical tree construction.

---

## 4. Invariants Preserved

* Structural consistency
* Deterministic hierarchy
* Backend neutrality
