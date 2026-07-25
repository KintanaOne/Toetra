# Type and Vocabulary Normalization Contract

> Status: P0 / Accepted target normalization  
> Scope: Vocabulary, scalar types, literal kinds and operator families  
> Audience: parser, builder, semantic, IR and ModelBridge maintainers

## Purpose

Normalization ensures that equivalent surface forms become stable internal values without erasing source meaning.

---

## Canonical Controlled Vocabulary

The target internal vocabulary includes enum-like values for:

- property types;
- backend names;
- quantifier kinds (`FORALL`, `EXISTS`);
- comparison operators;
- arithmetic operators;
- interval boundary kinds (`OPEN`, `CLOSED`);
- semantic scope kinds;
- verification semantics;
- assumption sources;
- normal-form kinds.

Aliases such as `∀` and `forall` normalize to the same quantifier kind while the original token may remain in source provenance.

---

## Scalar Types

Canonical scalar types include at least:

```text
INT
REAL
BOOL
STRING
NULL
SYMBOLIC_CATEGORY
UNKNOWN_MODEL_DEPENDENT
```

`SYMBOLIC_CATEGORY` is distinct from:

- a string literal;
- an input-feature reference;
- a variable identifier.

Example:

```toetra
x0.region: {EU, US}
```

contains two symbolic category literals.

---

## Literal Kinds

A scalar value preserves both value and literal kind.

| Source | Canonical value | Literal kind |
|---|---|---|
| `10` | `10` | integer |
| `10.5` | exact decimal/rational representation where possible | real |
| `true` | `True` | boolean |
| `"EU"` | `EU` | string |
| `EU` inside finite set | `EU` | symbolic category |
| `null` | `None` | null |

A builder must not identify symbolic categories only by `str` runtime type without a literal-kind discriminator.

---

## Numeric Promotion

The semantic layer applies one documented promotion policy.

Target baseline:

```text
INT +,-,* INT → INT
INT with REAL → REAL
REAL with REAL → REAL
numeric division → REAL
```

Backends may use exact rational values internally. Floating-point approximation is not introduced silently by normalization.

---

## Target Type

`target` obtains its scalar type from ModelSchema/model encoding when available.

Until resolved, it may carry an explicit model-dependent type marker, but backend compilation cannot guess its sort.

---

## Boundary Ownership

| Boundary | Responsibility |
|---|---|
| Parser | Preserve surface tokens and literal spelling. |
| Builder | Produce canonical vocabulary and typed literal nodes. |
| Semantic | Resolve scalar types, promotion and compatibility. |
| ModelBridge | Normalize feature/target dtypes. |
| IR1/IR2 | Preserve canonical types and requirements. |
| Backend | Map canonical types to backend sorts exactly. |

---

## Prohibited Normalizations

FORML must not:

- normalize an unknown explicit entity to the only variable in scope;
- normalize `{0, 7}` to `[0, 7]`;
- normalize `]0, 3[` to `[0, 3]`;
- normalize symbolic categories to feature references;
- normalize unsupported nonlinear arithmetic to affine arithmetic;
- normalize `exists` execution into universal refutation;
- coerce every feature to a real backend variable regardless of schema.

---

## Normalization-Owned Failures

- unknown controlled-vocabulary value;
- invalid literal token-to-kind mapping;
- incompatible scalar promotion;
- unresolved model-dependent type at backend boundary;
- unsupported external dtype mapping;
- ambiguous categorical encoding.

## Specification Constant Type Normalization

Specification-constant literal types are canonicalized at the builder/semantic boundary and preserved through IR:

```text
integer literal → INT
real literal    → FLOAT
boolean literal → BOOL
quoted string   → STRING
```

A use may still be rejected when its type is incompatible with the surrounding arithmetic, comparison, feature schema or backend capabilities.

FORML must not coerce a specification constant merely because a backend only supports a narrower sort family.
