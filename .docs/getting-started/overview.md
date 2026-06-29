# Getting Started with FORML

> Status: Draft  
> Scope: User onboarding  
> Implementation: Partial V1 path

## What is FORML?

FORML is a behavioral specification and verification framework for machine learning systems.

It provides a DSL and compiler pipeline for expressing properties that a model should satisfy, validating those properties semantically, transforming them into logical intermediate representations, and eventually lowering them into backend-specific verification queries.

The minimal V1 target is a Z3-based end-to-end path.

```text
.forml specification
+ model artifact
→ semantic validation
→ IR1 / NNF
→ IR2 / CNF-DNF
→ assertion aggregation
→ lowering / minimization
→ Z3 backend query
→ verification result
```

## Who is FORML for?

FORML is intended for people who need to reason about ML model behavior beyond ordinary metrics.

Examples include:

- ML engineers validating model constraints,
- ML platform engineers integrating verification in CI,
- researchers exploring formal methods for ML systems,
- teams that need model reliability, robustness, or behavioral guarantees.

## What problem does FORML solve?

Traditional ML validation often focuses on aggregate metrics:

```text
AUC
accuracy
precision
recall
loss
```

FORML focuses on behavioral properties:

```text
Is the model robust around a point?
Does a prediction stay bounded?
Is a property monotonic?
Are two related inputs treated consistently?
Does a model satisfy a declared logical property?
```

## Current implementation focus

The current implementation focuses on:

- DSL grammar and parsing,
- AST construction,
- semantic validation,
- symbol binding and implicit entity resolution,
- IR1 generation,
- initial logical normalization,
- ModelBridge foundations,
- Z3 as the minimal V1 backend target,
- documentation and contracts for the end-to-end path.

## What is not V1?

The following are not required for the first functional V1:

- ERAN backend,
- multi-backend orchestration,
- AutoFORML,
- runtime monitoring,
- distributed verification,
- advanced proof generation.

These are post-V1 extensions.

## Suggested reading path

Start with:

1. Architecture Overview
2. Pipeline Views
3. Compiler Pipeline
4. ModelBridge Overview
5. IR Overview
6. Contracts Overview
7. Testing Strategy
8. ADR Overview
