
---

# 📄 `implication.md`

```md
# Implication Parsing

## Purpose

FORML supports implication expressions inside assertions.

---

## Supported structure

Implications use the following structure:

```text
A -> B
```

## AST mapping

Parsed into:

`ImplicationNode`

## Core invariants
| Invariant                  | Description                              |
| -------------------------- | ---------------------------------------- |
| Binary structure           | Implication requires left/right operands |
| Stable ordering            | Left/right ordering must be preserved    |
| Nested implication support | Implications may contain implications    |
| Stable AST typing          | Implications must map to ImplicationNode |

## Supported cases
- simple implication
- nested implication
## Limitations

Implication associativity behavior is currently inferred from tests.

[TO_VERIFY]

## Tested by
| Test Cases                      |
| ------------------------------- |
| `test_logic_implication`        |
| `test_logic_nested_implication` |
