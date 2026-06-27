# `architecture/layers/ast.md`

# AST Layer

## 1. Purpose

The AST Layer is the semantic structuring layer of the FORML compilation pipeline.

Its role is to transform grammar-oriented CST structures into deterministic semantic-oriented abstract representations consumable by downstream semantic analysis stages.

The AST introduces structural meaning without yet performing semantic validation or execution reasoning.

---

## 2. Responsibilities

The AST Layer is responsible for:

- CST traversal,
- AST node construction,
- structural normalization,
- logical restructuring,
- scope extraction,
- assertion decomposition,
- expression normalization,
- deterministic hierarchy construction.

---

## 3. Non-Responsibilities

The AST Layer must NOT:

- resolve variable bindings,
- validate typing correctness,
- perform semantic validation,
- verify backend compatibility,
- execute symbolic reasoning,
- generate execution IR,
- normalize executable logic.

These concerns belong to downstream layers.

---

## 4. Architectural Position

```mermaid
flowchart LR

    A[.forml]
        --> B[Parsing Layer]
        --> C[CST]

    C
        --> D[AST Builder]

    D
        --> E[AST]
        --> F[Semantic Layer]
````

---

## 5. Input Contract

The AST Layer accepts:

* structurally valid CST representations,
* grammar-oriented parsing structures.

The AST Layer assumes:

* deterministic CST construction,
* successful syntax validation upstream.

---

## 6. Output Contract

The AST Layer guarantees:

* deterministic AST construction,
* normalized structural hierarchy,
* backend-agnostic semantic scaffolding,
* consistent logical representation.

The AST Layer does NOT guarantee:

* semantic correctness,
* typing validity,
* satisfiability,
* backend compatibility.

---

## 7. Invariants

### Structural Consistency

Logical structures must follow deterministic tree organization.

---

### Scope Isolation

Scopes must remain isolated between properties.

---

### Deterministic Construction

The same CST must always generate the same AST.

---

### Backend Neutrality

The AST must remain backend-agnostic.

---

### Pre-Semantic State

The AST must remain valid even with unresolved symbols.

---

## 8. Validation Philosophy

The AST Layer validates:

* structural consistency,
* logical hierarchy correctness,
* scope organization,
* expression normalization consistency.

The AST Layer intentionally defers:

* symbol resolution,
* type validation,
* semantic reasoning,
* execution compatibility.

---

## 9. Error Model

The AST Layer rejects:

* malformed logical hierarchies,
* inconsistent scope structures,
* invalid AST node organization,
* structurally invalid transformations.

The AST Layer may tolerate:

* unresolved symbols,
* incomplete semantic context,
* deferred bindings.

---

## 10. Important Architectural Distinction

| Layer    | Responsibility            |
| -------- | ------------------------- |
| Parsing  | Syntax correctness        |
| AST      | Structural semantics      |
| Semantic | Semantic validation       |
| IR       | Executable representation |

---

## 11. Layer Contracts

| Property            | Description |
| ------------------- | ----------- |
| Input               | CST         |
| Output              | AST         |
| Deterministic       | Yes         |
| Semantic Validation | No          |
| Backend Awareness   | No          |

---

## 12. Interaction With Adjacent Layers

### Upstream

Receives:

* CST structures,
* grammar-oriented representations.

### Downstream

Provides:

* normalized AST,
* structural semantic hierarchy,
* scope structures,
* logical structures.

---

## 13. Related Documents

| Document                               | Purpose                   |
| -------------------------------------- | ------------------------- |
| `../ast/ast_builder_pipeline.md`       | AST construction pipeline |
| `../ast/node_model.md`                 | AST node architecture     |
| `../ast/scope_model.md`                | Scope system              |
| `../ast/assertion_model.md`            | Logical assertions        |
| `../ast/expression_model.md`           | Expression structures     |
| `../ast/program_model.md`              | Program representation    |
| `../ast/cst_to_ast_transformations.md` | CST → AST transformations |
| `../ast/design_principles.md`          | AST design philosophy     |

---

## 14. Future Extensions

Potential future evolutions include:

* typed AST nodes,
* optimization hints,
* structural caching,
* symbolic placeholders,
* dependency graph integration,
* partial evaluation annotations.

---

## 15. Conclusion

The AST Layer forms the structural semantic backbone of the FORML pipeline.

It bridges syntactic parsing and semantic reasoning while remaining deterministic, normalized, backend-agnostic, and structurally consistent.
