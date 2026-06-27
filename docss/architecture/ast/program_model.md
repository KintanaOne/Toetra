# `architecture/ast/program_model.md`

# Program Model

## 1. Purpose

Define the top-level AST program representation.

---

## 2. Program Structure

```text
Program
 ├── Properties
 │     ├── Scope
 │     ├── Assertion
 │     └── Metadata
````

---

## 3. Responsibilities

The Program node organizes:

* property collections,
* metadata,
* global structural organization.

---

## 4. Characteristics

The Program representation remains:

* backend-agnostic,
* deterministic,
* structurally normalized.

---

## 5. Invariants

* Properties remain isolated.
* Program hierarchy remains acyclic.
* Metadata remains non-executable.
