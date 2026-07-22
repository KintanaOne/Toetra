# Model Constraints Contract

> Status: P0 / Planned / Critical  
> Scope: ModelSchema to model-derived logical constraints  
> Implementation: Not yet implemented  
> Audience: ModelBridge authors, backend authors, IR authors

## Purpose

The Model Constraints contract defines how ModelBridge information becomes logical constraints used by verification.

It answers the question:

```text
What logical constraints does the model contribute to the verification problem?
```

ModelBridge is not only a metadata provider. Its schema is the foundation for model-aware semantic validation and future model constraint generation.

---

## Input

```text
ModelSchema
+
optional model encoding strategy
```

The input may include:

- feature schema;
- target;
- task type;
- framework metadata;
- model type;
- backend capability information;
- symbolic encoding strategy.

---

## Output

```text
ModelConstraintSet
```

A model constraint set may include:

- feature existence constraints;
- dtype constraints;
- input dimensionality constraints;
- target/output constraints;
- model task constraints;
- future symbolic model behavior constraints.

---

## Constraint Families

| Constraint Family | Example |
|---|---|
| Feature constraints | `age` exists and is numeric. |
| Input constraints | model expects N input features. |
| Target constraints | target is `label`. |
| Task constraints | classification-compatible predicate. |
| Output constraints | class labels or regression output domain. |
| Symbolic model constraints | future model encoding for solver backends. |

---

## Relationship with Assertion Aggregation

Model constraints are not backend queries by themselves.

They are aggregated with:

- user DSL assertions;
- semantic constraints;
- scope constraints;
- domain constraints;
- neighborhood constraints;
- backend capability constraints.

The result is an `AggregatedAssertionSet`.

---

## Guarantees

If model constraint generation succeeds:

- constraints are traceable to ModelSchema metadata;
- constraints are backend-independent unless explicitly marked otherwise;
- constraints can be aggregated with DSL assertions;
- unsupported model encodings fail explicitly;
- no solver execution has occurred yet.

---

## Non-Goals

This contract must not:

- verify a property alone;
- choose CNF/DNF for the full query;
- minimize all assertions;
- encode final backend-specific objects unless delegated to backend lowering;
- silently invent missing model metadata.

---

## Failure Modes

Expected failures include:

- missing required feature metadata;
- unsupported model type for symbolic encoding;
- unsupported task type;
- incompatible backend capability;
- unrepresentable model operation;
- incomplete schema.

---

## Miova Hooks

Miova may mutate:

- feature metadata;
- model task;
- target name;
- model type;
- framework metadata;
- generated model constraints.

Expected outcomes:

| Mutation | Expected Boundary |
|---|---|
| Schema invalid | ModelBridge or schema-semantic rejection. |
| Constraint invalid | model-constraints rejection. |
| Constraint valid but challenging | aggregation/lowering continues. |

## Patch 21 Model Quantities and Observable Lowering

Patch 21 separates two contributions that were previously both described as
"output constraints":

1. **model quantities**, materialized by a ModelBridge encoder from a concrete
   model artifact, such as an affine latent decision value per evaluation;
2. **observable lowerings**, defined by a framework-neutral model semantic
   profile and connecting a public label/probability property to those quantities.

The encoder must not erase the public observable or define DSL vocabulary. The
backend receives only the canonical constraints after lowering, while reporting
and provenance retain both the source intention and the generated model
quantities.

See [Initial Binary Classification Profile](binary-classification-profile.md).
