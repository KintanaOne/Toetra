# Concrete Syntax Tree (CST)

## 1. Purpose

Represent the raw syntactic structure produced by parsing.

---

## 2. Responsibilities

The CST preserves:

- grammar hierarchy,
- token ordering,
- syntactic grouping,
- parsing context.

---

## 3. Characteristics

The CST may contain:

- intermediate grammar nodes,
- punctuation artifacts,
- helper structures,
- parsing-oriented hierarchy.

---

## 4. Invariants

- CST preserves syntactic organization.
- CST remains parser-oriented.
- CST is not semantically normalized.

---

## 5. Transition

The CST is consumed by the AST Builder layer.