# Header Parsing

## Purpose

The header defines global program configuration.

---

## Supported structure

The header currently supports:

- model declaration
- target declaration

---

## Example structure

```text
model := "model.onnx"
target := MyTarget
dataset := "folder/dataset.csv"
```

## Core invariants
| Invariant               | Description                        |
| ----------------------- | ---------------------------------- |
| Model required          | Header must define a model         |
| Target required         | Header must define a target        |
| Model type valid        | Model must be a string             |
| Target identifier valid | Target must be a valid identifier  |
| Stable ordering         | Header declarations preserve order |

## Supported comments

Comments inside the header are supported.

[TO_VERIFY]

## Valid cases
- minimal valid header
- header with comments
## Invalid cases
- missing model
- missing target
- missing both
- invalid model type
- invalid target type
## Tested by
| Test File        |
| ---------------- |
| `test_header.py` |
