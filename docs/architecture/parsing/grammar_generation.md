# Grammar Generation Pipeline

## 1. Purpose

Describe how the canonical FORML grammar is transformed into executable parser grammar artifacts.

---

## 2. Source of Truth

The canonical grammar definition is written using an EBNF-like notation.

Generated parser grammars are derived artifacts.

---

## 3. Pipeline Overview

```mermaid
flowchart TD

    A[EBNF Rules]
        --> B[Transformation Pipeline]

    B
        --> C[Generated Parser Grammar]
````

---

## 4. Transformation Stages

| Stage                    | Responsibility                      |
| ------------------------ | ----------------------------------- |
| Assignment Conversion    | Convert EBNF assignment syntax      |
| Bracket Protection       | Preserve escaped symbols            |
| Structure Transformation | Expand optional/repeated constructs |
| Placeholder Resolution   | Inject vocabulary fragments         |
| Formatting               | Stabilize grammar output            |

---

## 5. Invariants

* Grammar generation must be deterministic.
* Generated grammar must remain backend-agnostic.
* Vocabulary injection must remain reproducible.

---

## 6. Validation Guarantees

If generation succeeds:

* grammar output is deterministic,
* placeholders are resolved,
* grammar structure is normalized.
