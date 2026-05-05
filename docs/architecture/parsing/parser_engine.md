# Parser Engine

## 1. Purpose

Describe the parser engine responsible for applying generated grammar rules to `.forml` specifications.

---

## 2. Responsibilities

The parser engine is responsible for:

- tokenization,
- parse tree generation,
- ambiguity handling,
- syntax validation,
- parse diagnostics.

---

## 3. Parser Backend

Current implementation relies on:

```text
Lark Parser
````

This implementation detail may evolve independently from the Parsing Layer contract.

---

## 4. Invariants

* Parsing must remain deterministic.
* Grammar application must preserve token ordering.
* Syntax diagnostics must remain syntax-oriented.
