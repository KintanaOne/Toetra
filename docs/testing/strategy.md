# Testing Strategy

> Status: P0 — target testing strategy  
> Implementation: partially implemented  
> Scope: FORML compiler, ModelBridge, IR pipeline, backend boundary, and Miova campaigns

## Purpose

This document defines the testing strategy for FORML.

FORML is not tested as a single parser or as a set of isolated functions. It is tested as
a layered verification pipeline where each transformation introduces stronger guarantees
than the previous one.

The objective is to validate that FORML can safely transform a user specification and a
model representation into a backend-ready verification problem.

## Testing Philosophy

FORML testing is based on five principles:

1. **Layer isolation**
2. **Contract validation**
3. **Golden sample reproducibility**
4. **Expected failure classification**
5. **Mutation-driven robustness**

The purpose is not only to verify that the happy path works. FORML must also reject
invalid artifacts at the correct boundary, with the correct error category.

## Target End-to-End Path

The complete target pipeline is:

```text
.forml source
→ CST
→ AST
→ SemanticValidatedAST
→ IR1 / NNF
→ IR2 / CNF-DNF
→ ModelSchema
→ ModelConstraints
→ AggregatedAssertionSet
→ LoweredQuery
→ BackendQuery
→ VerificationResult
```

Testing must progressively cover every boundary in this path.

## Test Categories

| Category | Purpose | Priority |
|---|---|---:|
| Unit tests | Validate local behavior of small functions/classes | P0 |
| Layer tests | Validate one compiler layer in isolation | P0 |
| Contract tests | Validate input/output guarantees between layers | P0 |
| Property-Based Testing | Generate structured examples with Hypothesis | P0 |
| Intelligent fuzzing | Explore targeted adversarial and boundary cases | P0 |
| Golden samples | Freeze known valid and invalid examples | P0 |
| End-to-end tests | Validate complete query compilation path | P0 |
| Miova campaigns | Challenge artifacts through controlled mutations | P0 |
| Backend tests | Validate backend-specific encodings | P1 |
| Regression tests | Prevent previously fixed bugs from reappearing | P0 |
| Performance tests | Detect scaling issues in future workloads | P2 |

## Current Testing Focus

At the current stage, FORML should prioritize:

1. Source-to-CST stability
2. CST-to-AST correctness
3. semantic binding correctness
4. property/scope compatibility checks
5. IR1 generation
6. IR1 logical normalization
7. Property-Based Testing for generated valid/invalid programs
8. intelligent fuzzing of parser, semantic, IR, and schema boundaries
9. ModelBridge schema generation
10. schema-aware semantic validation
11. expected failure boundaries
12. Miova mutation campaigns on artifacts


## Property-Based Testing and Fuzzing

FORML should explicitly distinguish three related exploration layers:

| Layer | Tooling / method | Role |
|---|---|---|
| Property-Based Testing | Hypothesis strategies | Generate many structured valid and invalid examples |
| Intelligent fuzzing | Guided perturbation and boundary search | Discover adversarial, ambiguous, or late-failing cases |
| Miova campaigns | Artifact mutation with contracts and invariants | Challenge layer boundaries and classify mutation outcomes |

These approaches are complementary. Hypothesis explores input spaces, intelligent fuzzing searches for high-value boundary cases, and Miova validates artifact transitions through contracts, invariants, and expected failure classification.

## Layer Responsibilities

| Layer | What must be tested |
|---|---|
| Language | grammar acceptance/rejection, vocabulary normalization |
| Parser | CST generation, syntax failures |
| Builder | strict AST construction, missing node rejection |
| AST | structural invariants, node shape |
| Semantic | symbol binding, implicit entity resolution, scope compatibility |
| IR1 | logical tree translation, NNF invariants, semantic resolution preservation |
| IR2 | CNF/DNF generation, equivalence/equisatisfiability tracking |
| ModelBridge | loader selection, framework detection, introspection, ModelSchema shape |
| Aggregation | DSL assertions + semantic constraints + model constraints composition |
| Lowering | simplification, minimization, backend-preparation guarantees |
| Backend boundary | backend query shape and capability matching |
| Miova | controlled mutations, expected failures, invariant validation |

## Testing Status Vocabulary

Every test suite should be documented with one of the following statuses:

| Status | Meaning |
|---|---|
| implemented | Tests exist and are expected to pass |
| stabilizing | Tests exist but behavior may still evolve |
| planned | Tests are required but not implemented yet |
| blocked | Tests depend on an unfinished subsystem |
| research | Tests concern exploratory or future work |

## Expected Failure Policy

FORML should distinguish:

| Failure Type | Meaning |
|---|---|
| syntax failure | invalid source rejected by parser |
| build failure | valid CST cannot produce a valid AST |
| semantic failure | AST violates binding, scope, type, or compatibility rules |
| IR failure | semantic artifact cannot be translated into logical IR |
| model failure | model cannot be loaded, detected, or introspected |
| schema failure | ModelSchema does not satisfy semantic expectations |
| aggregation failure | logical/model constraints cannot be composed |
| lowering failure | query cannot be minimized or prepared |
| backend failure | backend cannot encode or execute the query |
| mutation rejection | Miova mutation is not applicable or violates invariants |

## Non-Goals

This strategy does not define:

- backend-specific proof algorithms;
- solver completeness guarantees;
- runtime performance benchmarks;
- production monitoring guarantees.

Those belong to backend, runtime, and observability documentation.

## Success Criteria

The testing strategy is considered effective when:

- each compiler boundary has explicit tests;
- each invalid artifact fails at the expected layer;
- golden samples cover every major property/scope combination;
- Miova can mutate artifacts without corrupting unrelated layers;
- end-to-end compilation can be validated deterministically;
- failures are classified precisely enough to support debugging and CI.

---

## Language Evolution Freeze

Before changing implementation, FORML freezes the expected behavior of explicit quantifiers, typed domains, scalar arithmetic and specification constants through stable example and test identifiers.

The mandatory gate sequence is:

```text
G1 parser baseline
→ G1.1 specification constants parser
→ G2 AST/builder
→ G3 semantic
→ G4 IR1
→ G5 IR2/aggregation
→ G6 backend
→ G7 end-to-end
```

The detailed matrix is defined in [Language Evolution Test Matrix](language-evolution-test-matrix.md).

A test must distinguish:

- invalid source;
- invalid semantic meaning;
- valid but unsupported backend requirement;
- verified universal property;
- universal counterexample;
- existential witness;
- absence of existential witness;
- inconclusive result;
- vacuous universal result.

The existing test suite remains a regression gate throughout the migration.


Detailed specification-constant test ownership is defined in [Specification Constants Test Plan](specification-constants-tests.md).
