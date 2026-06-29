# Open Questions

> Status: Active  
> Scope: Architecture and implementation questions

## Purpose

This document tracks questions that should remain explicit until the V1 architecture is fully stabilized.

Open questions are not weaknesses. They are intentional design boundaries.

## Compiler questions

### Should every AST node inherit from a common ASTNode?

Current direction:

```text
Prefer consistent ASTNode inheritance or explicit semantic-capable node typing.
```

Reason:

Semantic annotations should not be attached dynamically to nodes that do not declare support for them.

### Should SemanticValidatedAST be a new object or annotated AST?

Current direction:

```text
Use annotated AST for V1, consider explicit SemanticAST later.
```

Reason:

Annotated AST is simpler now, but an explicit semantic tree may become useful for advanced analysis.

## Language questions

### Should logical operators be uppercase or lowercase?

Current direction:

```text
User-facing syntax may support reasonable forms, internal representation must be canonical.
```

Examples:

```text
AND / and
OR / or
NOT / not
```

### How should quantifiers be normalized?

Current direction:

```text
∀ and forall should normalize to the same canonical enum.
∃ and exists should normalize to the same canonical enum.
```

## IR questions

### Does IR1 eliminate implications or preserve them?

Current direction:

```text
IR1 should move toward implication-normalized NNF.
```

The exact invariant should be documented and tested.

### Should CNF/DNF preserve equivalence or equisatisfiability?

Current direction:

```text
Prefer semantic equivalence when possible.
Allow equisatisfiability only when explicitly documented.
```

## ModelBridge questions

### Is a dataset required for feature detection?

Current direction:

```text
Either dataset_path or explicit schema should be required when the model cannot expose feature metadata.
```

### Should ModelSchema include output schema?

Current direction:

```text
Likely yes for richer verification, but V1 may start with features, target, task, and metadata.
```

## Assertion aggregation questions

### What is the exact AggregatedAssertionSet structure?

Current direction:

```text
It should preserve user assertions, semantic constraints, model constraints, and provenance separately.
```

### Should contradictions be detected during aggregation or lowering?

Current direction:

```text
Basic contradictions can be detected during aggregation.
Solver-aware simplification belongs closer to lowering/backend preparation.
```

## Lowering questions

### How aggressive should minimization be?

Current direction:

```text
V1 should prefer safe simplification over aggressive optimization.
```

Reason:

Correctness and traceability are more important than maximum optimization in V1.

## Backend questions

### Should FORML support ERAN in V1?

Decision:

```text
No. Z3 is the minimal V1 backend.
ERAN and other backends are post-V1 extensions.
```

### Should backend orchestration be implemented before Z3 works?

Decision:

```text
No. The backend boundary should be documented, but orchestration can wait.
```

## Testing questions

### What belongs to Hypothesis vs Miova?

Current direction:

```text
Hypothesis generates structured examples.
Miova mutates typed artifacts and validates contracts/invariants.
```

### Should fuzzing happen only at source level?

Current direction:

```text
No. FORML should eventually support source, AST, semantic AST, IR, ModelSchema, and aggregated assertion fuzzing/mutation.
```

## Documentation questions

### Should future features be documented now?

Decision:

```text
Yes, if they are required by the end-to-end architecture.
But they must be clearly marked as planned or post-V1.
```

### Should SMS still appear in the docs?

Current direction:

```text
Only as historical inspiration if needed.
The current product/system name should be Miova.
```
