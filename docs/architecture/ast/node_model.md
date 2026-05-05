# `architecture/ast/node_model.md`

# AST Node Model

## 1. Purpose

Define the conceptual node categories composing the AST.

---

## 2. Core Node Categories

```text
1. Scope Nodes
2. Expression Nodes
3. Assertion Nodes
4. Program Nodes
````

---

## 3. Scope Nodes

Represent semantic context:

* variable roles,
* domain constraints,
* neighborhood definitions,
* quantifier structures.

---

## 4. Expression Nodes

Represent structured references:

* attributes,
* constants,
* feature access,
* symbolic references.

---

## 5. Assertion Nodes

Represent logical structures:

* comparisons,
* conjunctions,
* disjunctions,
* negations,
* implications.

---

## 6. Program Nodes

Top-level program representation:

```text
Program
 ├── Properties
 │     ├── Scope
 │     ├── Assertion
 │     └── Metadata
```

---

## 7. Invariants

* Node hierarchy must remain acyclic.
* Logical structures must remain deterministic.
* Program organization must remain normalized.