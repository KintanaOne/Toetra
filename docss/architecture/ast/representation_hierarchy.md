# `architecture/ast/representation_hierarchy.md`

# Representation Hierarchy

## 1. Purpose

Describe the progression of FORML representations across the pipeline.

---

## 2. Hierarchy Overview

```mermaid
flowchart LR

    A[CST]
        --> B[AST]
        --> C[Semantic IR]
        --> D[Backend IR]
````

---

## 3. Representation Roles

| Layer       | Nature              |
| ----------- | ------------------- |
| CST         | syntactic           |
| AST         | structural semantic |
| Semantic IR | validated semantic  |
| Backend IR  | executable semantic |

---

## 4. Architectural Philosophy

Each representation introduces:

* stronger guarantees,
* reduced ambiguity,
* increased semantic precision,
* more constrained structures.

---

## 5. Invariants

* Representations remain deterministic.
* Guarantees accumulate progressively.
* Semantic precision increases downstream.