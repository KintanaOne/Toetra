# Type Normalization Contract

> Status: P0 / Needs Stabilization  
> Scope: enum, dtype, value and symbolic type normalization  
> Implementation: partially implemented across vocabulary, builder, semantic and ModelBridge  
> Audience: compiler maintainers, semantic maintainers, ModelBridge authors

## Purpose

The Type Normalization contract defines how FORML converts raw values, strings and framework metadata into stable internal types.

It answers the question:

```text
When two layers say the same thing differently, what is the canonical form?
```

Without a normalization contract, small spelling/casing differences can break the compiler.

---

## Normalization Targets

| Category | Examples |
|---|---|
| Properties | `ROBUSTNESS`, `BOUND`, `FAIRNESS` |
| Problems | `CLASSIFICATION`, `REGRESSION` |
| Functions | `EQUAL`, `BETWEEN`, `INCREASING` |
| Backends | `z3`, `Z3`, `ERAN` |
| Metrics | `L1`, `L2`, `Linf` |
| Quantifiers | `forall`, `exists`, `∀`, `∃` |
| Comparison operators | `==`, `!=`, `<`, `<=`, `>`, `>=` |
| Data types | `int`, `float`, `bool`, `string`, `none` |
| Model tasks | `classification`, `regression`, `unknown` |

---

## Canonicalization Principle

At every boundary, FORML should convert raw values into canonical internal representations.

Preferred canonical forms:

- enums for controlled vocabularies;
- explicit dtype enum for data types;
- lowercase normalized strings only when enum is not appropriate;
- structured dataclasses for model schema and IR artifacts.

---

## Boundary Rules

| Boundary | Normalization Responsibility |
|---|---|
| Parser | Preserve raw syntax. |
| Builder | Convert tokens to AST values/enums where possible. |
| Semantic | Normalize and validate enums before compatibility checks. |
| ModelBridge | Normalize framework, task and feature dtypes. |
| IR1 | Preserve normalized enum values. |
| IR2 | Preserve logical operator semantics. |
| Backend | Convert canonical FORML types to backend types. |

---

## Value Parsing

Constants should preserve both:

- raw parsed value;
- inferred semantic dtype.

Examples:

| Source | Value | Type |
|---|---|---|
| `10` | `10` | int |
| `10.5` | `10.5` | float |
| `true` | `True` | bool |
| `"A"` | `A` | string |

---

## Feature Type Normalization

ModelBridge maps external framework types into FORML semantic types.

Examples:

| External dtype | FORML dtype |
|---|---|
| pandas int dtype | `INT` |
| pandas float dtype | `FLOAT` |
| pandas bool dtype | `BOOL` |
| object/string dtype | `STRING` |

---

## Stabilization Notes

The contract should stabilize:

- backend enum normalization;
- quantifier normalization;
- metric values without embedded quotes;
- property and problem enum handling;
- function compatibility handling;
- casing policy for logical operators;
- schema task names.

---

## Failure Modes

This layer should reject:

- unknown enum values;
- unsupported dtype conversions;
- invalid quantifier aliases;
- operator/value incompatibilities;
- model tasks not supported by a property;
- backend names not known to FORML.

---

## Miova Hooks

Miova may mutate:

- enum casing;
- backend aliases;
- dtype values;
- metric spelling;
- quantifier symbols;
- task labels;
- comparison operators.

Expected outcome:

```text
Known alias      → normalized
Unknown value    → normalization rejection
Valid new value  → downstream layer may continue
```
