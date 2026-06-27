# Parsing Layer

## 1. Purpose

The Parsing Layer is the entry point of the FORML compilation pipeline.

Its role is to transform raw `.forml` specifications into deterministic syntactic structures consumable by downstream compilation stages.

The Parsing Layer is intentionally restricted to syntax-oriented concerns.

---

## 2. Responsibilities

The Parsing Layer is responsible for:

- tokenization,
- grammar application,
- syntax validation,
- CST generation,
- syntax-oriented diagnostics,
- ambiguity resolution,
- syntactic hierarchy preservation.

---

## 3. Non-Responsibilities

The Parsing Layer must NOT:

- resolve symbols,
- validate semantic correctness,
- perform type checking,
- normalize logic,
- generate execution plans,
- interpret backend semantics,
- optimize expressions.

These concerns belong to downstream layers.

---

## 4. Architectural Position

```mermaid
flowchart LR

    A[.forml]
        -->|Parsing Layer| B[CST]

    B
        -->|AST Builder| C[AST]
````

---

## 5. Input Contract

The Parsing Layer accepts:

* UTF-8 encoded `.forml` specifications,
* grammar-conforming token streams.

The layer assumes:

* accessible source text,
* deterministic grammar configuration.

---

## 6. Output Contract

The Parsing Layer guarantees:

* deterministic CST generation,
* preserved token ordering,
* preserved syntactic hierarchy,
* grammar-conforming parse structures.

The Parsing Layer does NOT guarantee:

* semantic correctness,
* typing validity,
* backend compatibility.

---

## 7. Invariants

### Grammar Determinism

A valid specification must always generate the same CST.

---

### Syntax Isolation

The Parsing Layer must remain isolated from semantic interpretation.

---

### Structural Preservation

The CST must preserve syntactic organization.

---

### Backend Independence

The Parsing Layer must remain backend-agnostic.

---

## 8. Validation Model

The Parsing Layer validates:

* grammar conformity,
* delimiter correctness,
* token placement,
* syntactic hierarchy,
* ambiguity resolution.

---

## 9. Error Model

The Parsing Layer reports:

* malformed syntax,
* tokenization failures,
* invalid delimiters,
* unsupported syntax patterns,
* grammar violations.

Errors produced by this layer must remain syntax-oriented.

---

## 10. Progressive Validation Philosophy

FORML applies layered validation.

Each layer strengthens guarantees before forwarding artifacts downstream.

```mermaid
flowchart LR

    A[Parsing]
        --> B[AST Validation]

    B
        --> C[Semantic Validation]

    C
        --> D[IR Validation]

    D
        --> E[Backend Validation]
```

---

## 11. Layer Contracts

| Property           | Description            |
| ------------------ | ---------------------- |
| Input              | `.forml` specification |
| Output             | CST                    |
| Deterministic      | Yes                    |
| Semantic Awareness | No                     |
| Backend Awareness  | No                     |

---

## 12. Interactions With Adjacent Layers

### Upstream

Receives raw `.forml` specifications.

### Downstream

Provides CST structures to the AST Builder layer.

---

## 13. Related Documents

| Document                            | Purpose                          |
| ----------------------------------- | -------------------------------- |
| `../parsing/grammar_generation.md`  | Grammar generation pipeline      |
| `../parsing/parser_engine.md`       | Parser engine details            |
| `../parsing/vocabulary_registry.md` | Vocabulary registry architecture |
| `../parsing/cst.md`                 | CST representation               |
| `ast.md`                            | AST layer                        |

---

## 14. Future Extensions

Potential future evolutions include:

* incremental parsing,
* IDE integration,
* grammar versioning,
* dialect support,
* advanced diagnostics.
