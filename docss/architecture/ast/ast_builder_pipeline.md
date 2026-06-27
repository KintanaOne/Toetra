# `architecture/ast/ast_builder_pipeline.md`

# AST Builder Pipeline

## 1. Purpose

Describe the transformation pipeline responsible for constructing the AST from CST structures.

---

## 2. Pipeline Overview

```mermaid
flowchart TD

    A[CST]
        --> B[AST Builder Pipeline]

    B --> C[Expression Normalizer]
    B --> D[Scope Extractor]
    B --> E[Assertion Builder]
    B --> F[Logical Structurer]

    C --> G[AST]
    D --> G
    E --> G
    F --> G
````

---

## 3. Pipeline Stages

### CST Traversal

Traverse grammar-oriented CST structures.

---

### Node Mapping

Map CST nodes into AST equivalents.

---

### Scope Extraction

Extract variable context and semantic scope.

---

### Expression Normalization

Normalize expression structures.

---

### Logical Structuring

Build deterministic logical hierarchies.

---

## 4. Invariants

* Construction must remain deterministic.
* Structural hierarchy must remain valid.
* Backend neutrality must be preserved.