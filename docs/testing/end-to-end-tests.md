# End-to-End Tests

> Status: P0 — target / partially blocked  
> Implementation: planned  
> Scope: full FORML request compilation and future verification execution

## Purpose

End-to-end tests validate that a FORML request can travel through the complete target path:

```text
.forml source
+ model artifact
→ compiler pipeline
→ ModelBridge
→ semantic/model integration
→ IR1
→ IR2
→ assertion aggregation
→ lowering/minimization
→ backend query
→ verification result
```

At the current stage, the full runtime path may not be implemented yet. However, the
end-to-end test design should be defined now so that each new subsystem plugs into a
stable expectation.

## End-to-End Levels

FORML end-to-end testing should be split into levels.

| Level | Scope | Status |
|---|---|---|
| E2E-0 | Source → IR1 | implemented / stabilizing |
| E2E-1 | Source + Model → SemanticValidatedAST + ModelSchema | planned / critical |
| E2E-2 | Source + Model → IR2 | planned |
| E2E-3 | Source + Model → AggregatedAssertionSet | planned |
| E2E-4 | Source + Model → LoweredQuery | planned |
| E2E-5 | Source + Model → BackendQuery | planned |
| E2E-6 | Source + Model → VerificationResult | future |

## E2E-0: Source to IR1

### Purpose

Validate the current compiler path:

```text
.forml source
→ CST
→ AST
→ SemanticValidatedAST
→ IR1 VerificationTask
```

### Expected Guarantees

- source parses successfully;
- AST is built;
- semantic validation succeeds;
- IR1 is generated;
- semantic resolution is preserved in IR1;
- logical structure is represented in backend-independent form.

### Required Cases

```text
local robustness
pointwise bound
pairwise monotonicity
quantifier property
logical composition
problem predicate
backend declaration
```

## E2E-1: Source + Model to Semantic + Schema

### Purpose

Validate that a FORML source and a real model artifact can be interpreted together.

```text
.forml source
+ model path
→ ProgramNode
+ ModelSchema
→ schema-aware semantic validation
```

### Expected Guarantees

- model artifact is loadable;
- framework is detected;
- features are introspected;
- DSL feature references exist in `ModelSchema`;
- model task is compatible with problem/property intent.

### Failure Cases

```text
missing model file
unsupported model format
unsupported model framework
feature referenced in DSL but missing in ModelSchema
classification predicate used with regression model
numeric comparison used on string feature
```

## E2E-2: Source + Model to IR2

### Purpose

Validate the planned logical normal-form pipeline.

```text
SemanticValidatedAST
→ IR1-NNF
→ IR2-CNF/DNF
```

### Expected Guarantees

- IR1 is already normalized or normalizable;
- IR2 form is selected according to verification strategy;
- CNF/DNF generation preserves semantic meaning or tracks equisatisfiability;
- traceability to original assertions remains available.

## E2E-3: Aggregated Assertion Set

### Purpose

Validate composition of:

```text
DSL assertions
+ semantic constraints
+ scope constraints
+ model constraints
```

### Expected Guarantees

- constraints are aggregated without losing origin metadata;
- contradictions are detected or represented;
- aggregation remains backend-independent.

## E2E-4: Lowered Query

### Purpose

Validate simplification and minimization before backend-specific encoding.

### Expected Guarantees

- redundant assertions are removed;
- tautologies are simplified;
- contradictions are preserved as diagnostics;
- simplifications remain traceable.

## E2E-5: Backend Query

### Purpose

Validate that a lowered query can be encoded for a selected backend.

### Expected Guarantees

- backend capabilities are checked;
- backend-specific query is deterministic;
- unsupported features fail before backend execution;
- query preserves the verification intent.

## E2E-6: Verification Result

### Purpose

Validate the full runtime path once backend execution exists.

### Expected Guarantees

- backend query executes;
- result is normalized;
- counterexamples are represented when available;
- diagnostics are meaningful;
- traces are linked to source assertions.

## Recommended Test Harness

A future E2E test harness should expose a function similar to:

```python
result = compile_forml_request(
    source=source,
    model_path=model_path,
    dataset_path=dataset_path,
    backend="z3",
)
```

The result should expose intermediate artifacts:

```python
result.cst
result.ast
result.semantic_ast
result.model_schema
result.ir1
result.ir2
result.aggregated_assertions
result.lowered_query
result.backend_query
result.verification_result
```

This makes E2E failures inspectable.

## Snapshot Policy

End-to-end tests should snapshot normalized artifacts, not Python reprs.

Recommended snapshot formats:

```text
json
yaml
canonical markdown debug output
```

Snapshots should include:

- artifact kind;
- layer;
- normalized payload;
- diagnostics;
- source trace references;
- status.

## End-to-End and Miova

Miova should extend E2E testing by mutating artifacts at different stages and verifying
that the pipeline reacts correctly.

Examples:

```text
mutate valid source → parser or semantic expected failure
mutate AST binding → semantic or IR expected failure
mutate IR1 logical operator → IR2 invariant failure
mutate ModelSchema dtype → schema-semantic failure
mutate AggregatedAssertionSet → lowering failure or diagnostic
```

## Success Criteria

End-to-end tests are sufficient when:

- at least one valid source/model pair reaches IR1;
- at least one valid source/model pair reaches schema-aware validation;
- every planned layer has a placeholder test or expected future test;
- failure boundaries are explicit;
- intermediate artifacts are inspectable;
- future backend execution can be added without redesigning the test strategy.

---

## Mandatory Quantified Solver Scenarios

The first executable language profile requires at least these solver-backed tests:

| Scenario | Expected result |
|---|---|
| true universal affine bound | VERIFIED |
| false universal affine bound | COUNTEREXAMPLE |
| satisfiable existential affine request | WITNESS |
| impossible existential affine request | NO_WITNESS |
| empty universal admissible set | structured vacuity warning |
| valid nonlinear request on affine-only backend | capability rejection before solver |
| valid categorical domain on numeric-only backend | capability rejection before solver |

The result model must be semantics-aware:

```text
SAT + universal refutation  → COUNTEREXAMPLE
UNSAT + universal refutation → VERIFIED
SAT + existential witness   → WITNESS
UNSAT + existential witness → NO_WITNESS
```

Tests must assert both normalized result status and solver status. They must also inspect returned valuations for counterexamples and witnesses.
