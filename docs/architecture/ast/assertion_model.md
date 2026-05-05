# `architecture/ast/assertion_model.md`

# Assertion Model

## 1. Purpose

Define logical structures representing FORML properties.

---

## 2. Responsibilities

Assertions encode:

- logical constraints,
- comparisons,
- implications,
- boolean composition.

---

## 3. Supported Logical Constructs

- AND
- OR
- NOT
- IMPLICATION

---

## 4. Assertion Tree Structure

Assertions form logical trees.

```mermaid
flowchart TD

    A[AND]
        --> B[Comparison]

    A
        --> C[OR]

    C
        --> D[Comparison]
    C
        --> E[NOT]
````

---

## 5. Invariants

* Logical hierarchy remains valid.
* Unary operators remain normalized.
* Assertion structures remain deterministic.
