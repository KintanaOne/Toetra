# End-to-End Preview

> Status: Target architecture  
> Scope: V1 path preview  
> Implementation: Partial

## Purpose

This page previews the intended end-to-end FORML V1 flow.

The goal is not to claim that every stage is fully implemented today, but to define the target path that the implementation should converge toward.

## Minimal V1 target

The minimal V1 path is:

```text
.forml specification
+ serialized ML model
+ optional dataset/schema
→ parsed CST
→ built AST
→ SemanticValidatedAST
→ IR1 / NNF
→ IR2 / CNF-DNF
→ AggregatedAssertionSet
→ LoweredQuery
→ Z3 BackendQuery
→ Z3 VerificationResult
```

## Step 1 — User writes a property

```forml
model := "model.joblib"
target := prediction

[ROBUSTNESS]: at x in neighborhood(metric=L2, eps=0.1)
=> CLASSIFICATION.EQUAL()
using z3
```

## Step 2 — FORML parses the source

The parser transforms source text into a CST.

```text
.forml source → CST
```

## Step 3 — FORML builds the AST

The builder converts syntax into typed AST nodes.

```text
CST → AST
```

## Step 4 — Semantic validation

Semantic validation resolves:

- scope,
- variables,
- implicit entities,
- symbol bindings,
- property/scope compatibility,
- problem/function compatibility.

```text
AST → SemanticValidatedAST
```

## Step 5 — IR1 / NNF

IR1 converts semantic logic into a backend-independent logical representation.

IR1 is responsible for early normalization such as De Morgan and NNF.

```text
SemanticValidatedAST → IR1
```

## Step 6 — IR2 / CNF-DNF

IR2 is planned as the normal-form layer.

It selects CNF or DNF depending on verification needs.

```text
IR1 → IR2
```

## Step 7 — ModelBridge

The model is loaded and introspected.

```text
model artifact → ModelSchema
```

ModelSchema then supports:

- schema-aware validation,
- model constraint preparation,
- future backend lowering.

## Step 8 — Assertion aggregation

FORML combines:

- user assertions,
- semantic constraints,
- scope constraints,
- domain constraints,
- neighborhood constraints,
- model-derived constraints.

```text
IR2 + ModelConstraints → AggregatedAssertionSet
```

## Step 9 — Lowering and minimization

The aggregated assertion set is simplified and prepared for backend encoding.

```text
AggregatedAssertionSet → LoweredQuery
```

## Step 10 — Z3 backend query

The lowered query is encoded into a Z3-specific backend artifact.

```text
LoweredQuery → Z3 BackendQuery
```

## Step 11 — Verification result

Z3 executes the query and returns a structured verification result.

```text
Z3 BackendQuery → VerificationResult
```

## Post-V1 extensions

The following are post-V1:

- ERAN backend,
- multi-backend orchestration,
- AutoFORML,
- runtime monitoring,
- distributed verification,
- advanced formal proof generation.

## Testing strategy

The end-to-end path should be validated through:

- golden samples,
- contract tests,
- property-based testing with Hypothesis,
- intelligent fuzzing,
- Miova mutation campaigns.
