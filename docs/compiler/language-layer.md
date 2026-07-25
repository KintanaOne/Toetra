# Language Layer

> Status: P0 / Stabilizing  
> Scope: DSL vocabulary and grammar boundary  
> Implementation: Implemented, needs normalization cleanup  
> Audience: DSL maintainers, compiler contributors, test authors

## Purpose

The language layer defines the expressive boundary of FORML.

It answers the question:

```text
What can a user express in a `.toetra` specification?
```

The language layer is responsible for:

- official vocabulary;
- grammar rules;
- syntax categories;
- property declarations;
- scope declarations;
- assertion expressions;
- backend hints;
- model and target declarations.

It is the first contract of the compiler pipeline.

---

## Responsibilities

The language layer defines:

| Concern | Responsibility |
|---|---|
| Vocabulary | Define official properties, problems, functions, metrics, backends and operators. |
| Grammar | Define legal Toetra source syntax. |
| Tokens | Define lexical units such as identifiers, strings, numbers and operators. |
| Property syntax | Define how properties are declared and scoped. |
| Assertion syntax | Define boolean and comparison expressions. |
| Header syntax | Define model, target and optional dataset declarations. |

---

## Current Language Concepts

FORML currently supports the following major language concepts.

### Header

A Toetra program starts with declarations such as:

```toetra
model := "model.joblib"
target := label
```

Future or optional declarations may include:

```toetra
dataset := "dataset.csv"
```

The header provides model-level context to be resolved later through ModelBridge.

---

### Property Sections

A property section defines a behavioral property to verify.

Conceptually:

```toetra
[PROPERTY_TYPE]: scope => assertion using backend(...)
```

Examples of property types include:

- `ROBUSTNESS`
- `STABILITY`
- `FAIRNESS`
- `MONOTONICITY`
- `BOUND`
- `LOGIC`

---

### Scopes

Scopes define where or how a property is evaluated.

FORML currently distinguishes:

| Scope | Meaning |
|---|---|
| `check_at` | Pointwise evaluation. |
| `at` | Local neighborhood evaluation around an anchor. |
| `pairwise` | Pairwise relation between an anchor and a perturbation. |
| `forall` / `exists` | Quantified symbolic evaluation. |

---

### Assertions

Assertions define what must hold.

They may contain:

- comparisons;
- boolean operators;
- implications;
- problem-level predicates;
- parentheses.

Examples:

```toetra
age <= 30
x.score >= 0.8
NOT risk > 0.5
age > 18 AND score >= 0.7
CLASSIFICATION.EQUAL()
```

---

### Backend Hints

Backend hints specify the verification backend or abstract domain preferred by the user.

Example:

```toetra
using z3()
```

A backend hint is not the same as backend orchestration. It is a user preference or constraint that later layers must validate against property requirements and backend capabilities.

---

## Language Layer Output

The language layer does not produce runtime objects directly.

It produces a grammar and vocabulary consumed by the parser.

```text
Vocabulary + Grammar
    ↓
Parser configuration
    ↓
CST production
```

---

## Normalization Requirements

The language layer must define canonical forms for values that can appear in multiple spellings.

Examples:

| Concept | Possible Inputs | Canonical Form |
|---|---|---|
| Backend | `z3`, `Z3` | `Z3` or canonical enum value |
| Quantifier | `∀`, `forall` | `forall` |
| Boolean operators | `AND`, `and` | one canonical operator form |
| Metric | `Linf`, `LINF` | canonical metric enum |

Without a normalization policy, downstream layers become fragile.

---

## Guarantees

The language layer must guarantee:

- every official DSL construct is expressible in grammar;
- grammar and enum vocabulary stay aligned;
- syntax does not accidentally encode semantic meaning;
- syntax variants can be normalized before semantic validation;
- future grammar extensions are explicit and testable.

---

## Non-Goals

The language layer must not:

- resolve variables;
- validate property-scope compatibility;
- inspect model schemas;
- decide backend compatibility;
- produce IR;
- perform logical rewriting.

Those responsibilities belong to later compiler layers.

---

## Known Stabilization Points

| Topic | Issue |
|---|---|
| Logic operator casing | Grammar and vocabulary must agree on `AND/OR/NOT` vs `and/or/not`. |
| Quantifier normalization | Unicode and word forms need a canonical representation. |
| Backend enum normalization | Lowercase and uppercase backend names must map consistently. |
| Metric enum values | Metric values should not contain accidental quotes. |
| `logic_expr` vs `comparison_expr` | The language should clarify whether non-comparison logical operations on attributes are supported. |

---

## Relation to Miova

Miova may mutate the source language layer to test parser robustness.

Examples:

- invalid property names;
- malformed scopes;
- unsupported operators;
- broken backend declarations;
- ambiguous identifiers;
- casing variants;
- missing header declarations.

These mutations should either be accepted and normalized or rejected at the parser/builder boundary with clear diagnostics.
