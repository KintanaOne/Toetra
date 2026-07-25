# Intelligent Fuzzing

> Status: P0 — planned / critical  
> Implementation: planned, complementary to Hypothesis and Miova  
> Scope: adversarial exploration of Toetra source, compiler artifacts, semantic boundaries, IR normal forms, model schemas, and backend queries

## Purpose

Intelligent fuzzing is the targeted exploration of FORML inputs and artifacts in order to discover weaknesses that random generation or static golden samples may miss.

In FORML, fuzzing should not be limited to malformed source strings. The system is layered, so fuzzing can target multiple representations:

```text
source string
CST
AST
SemanticValidatedAST
IR1
IR2
ModelSchema
ModelConstraints
AggregatedAssertionSet
LoweredQuery
BackendQuery
```

The objective is to find boundary failures, ambiguous semantics, unexpected crashes, invalid acceptances, and hidden assumptions inside the compiler and verification pipeline.

## Difference from Property-Based Testing

Property-Based Testing and fuzzing overlap, but they are not the same.

| Approach | Main idea | FORML use |
|---|---|---|
| Property-Based Testing | generate many structured examples from explicit strategies | validate general properties of the compiler |
| Random fuzzing | generate noisy or malformed inputs | test parser and error robustness |
| Intelligent fuzzing | generate targeted perturbations guided by structure, coverage, contracts, or failures | discover high-value boundary bugs |
| Miova campaigns | mutate typed artifacts with contracts and invariants | validate artifact transitions and expected failures |

FORML should use intelligent fuzzing as a targeted search process, not as blind random noise.

## Why FORML Needs Intelligent Fuzzing

FORML has several risk zones:

- grammar ambiguity;
- casing and vocabulary normalization;
- implicit entity resolution;
- property/scope compatibility;
- problem/function compatibility;
- semantic annotations attached after parsing;
- IR1 NNF invariants;
- IR2 CNF/DNF shape guarantees;
- ModelSchema feature alignment;
- aggregation of DSL assertions and model constraints;
- backend capability mismatch.

These risks are not always discovered by hand-written test.

Intelligent fuzzing helps find cases such as:

```text
syntactically valid but semantically ambiguous source;
valid AST with unresolved implicit entity;
IR1 tree that looks valid but violates NNF;
ModelSchema that passes shape checks but conflicts with DSL features;
aggregation that silently drops constraints;
lowering that simplifies away a required assertion.
```

## Fuzzing Levels

### 1. Source-Level Fuzzing

Target:

```text
.toetra source
```

Examples:

- mutate brackets;
- change operator casing;
- alter `=>` or `->`;
- remove model or target declaration;
- inject unknown property types;
- mutate backend names;
- reorder declarations;
- insert comments and whitespace noise.

Expected result:

```text
Parser accepts valid variants and rejects invalid variants cleanly.
```

### 2. Grammar-Aware Fuzzing

Grammar-aware fuzzing generates strings that remain close to the grammar.

Examples:

```text
[ROBUSTNESS]: forall baseline, candidate => CLASSIFICATION.EQUAL()
[BOUND]: check_at x => age <= 30
[MONOTONICITY]: x ~ x' in neighborhood(metric=L1, eps=1) => score >= 0
```

Then perturbations are applied while preserving partial grammar structure.

This is more useful than pure random string fuzzing because FORML is a structured DSL.

### 3. AST-Level Fuzzing

Target:

```text
forml.ast
```

Examples:

- remove assertion root;
- replace scope node with incompatible scope;
- flip property type;
- erase backend args;
- mutate comparison operators;
- replace attribute path with invalid path.

Expected result:

```text
AST contracts and semantic validation reject invalid structures.
```

### 4. Semantic Boundary Fuzzing

Target:

```text
forml.semantic_ast
```

Examples:

- remove `SemanticAnnotations`;
- corrupt `resolved_entity`;
- remove `SymbolTable` entries;
- change default entity;
- mismatch scope type and variables;
- alter problem/function compatibility after validation.

Expected result:

```text
Semantic-to-IR1 boundary rejects inconsistent semantic artifacts.
```

### 5. IR Fuzzing

Targets:

```text
forml.ir1
forml.ir2
```

Examples:

- introduce `NotIR` above non-atomic expressions after NNF;
- retain implication after implication elimination;
- break CNF clause shape;
- break DNF case shape;
- mix backend-specific expressions into IR2 too early;
- remove equivalence/equisatisfiability metadata.

Expected result:

```text
IR invariants reject malformed logical representations.
```

### 6. ModelBridge Fuzzing

Target:

```text
ModelSchema
```

Examples:

- remove target;
- mutate feature dtype;
- remove feature referenced by DSL;
- alter task type;
- corrupt framework metadata;
- mismatch number of model inputs and schema features.

Expected result:

```text
Schema-to-semantic or model-constraints validation detects mismatch.
```

### 7. Aggregation and Lowering Fuzzing

Targets:

```text
AggregatedAssertionSet
LoweredQuery
```

Examples:

- duplicate contradictory constraints;
- drop model constraints;
- remove traceability metadata;
- simplify expressions unsafely;
- merge constraints from incompatible scopes;
- remove backend capability requirements.

Expected result:

```text
Aggregation, lowering, or backend boundary detects inconsistency.
```

## Intelligent Guidance Signals

Intelligent fuzzing should be guided by signals.

| Signal | Meaning |
|---|---|
| coverage | which grammar rules or compiler branches were exercised |
| contract boundary | which layer should accept or reject the artifact |
| invariant violation | which invariant was broken |
| failure novelty | whether the failure is new or already known |
| shrinkability | whether the failing case can be minimized |
| semantic distance | how far the mutation is from the original artifact |
| layer depth | how far the artifact travels before rejection |

The most valuable fuzzing cases are not necessarily the most corrupted. They are often small, valid-looking artifacts that fail late or are incorrectly accepted.

## Intelligent Fuzzing and Miova

Miova is the natural execution layer for structured FORML fuzzing.

Miova can represent fuzzing operations as controlled mutations:

```text
Artifact + Mutation + Contract + Invariants → MutationResult
```

This allows fuzzing to be classified:

```text
SUCCESS
SKIPPED
REJECTED
FAILED
```

A blind fuzzer may only say “this crashed”. Miova should say:

```text
this mutation violated the AST-to-Semantic contract;
this mutation was correctly rejected;
this mutation unexpectedly passed;
this mutation failed outside its expected boundary.
```

## Fuzzing Campaign Types

Recommended intelligent fuzzing campaign families:

| Campaign | Target | Purpose |
|---|---|---|
| grammar fuzzing | source | grammar robustness |
| semantic ambiguity fuzzing | AST / Semantic AST | binding and scope resolution |
| compatibility fuzzing | property/scope/problem/function | rejection matrix |
| IR normal-form fuzzing | IR1 / IR2 | NNF/CNF/DNF invariants |
| schema mismatch fuzzing | ModelSchema | feature/task compatibility |
| aggregation fuzzing | AggregatedAssertionSet | composition correctness |
| lowering fuzzing | LoweredQuery | minimization safety |
| backend boundary fuzzing | BackendQuery | capability rejection |

## Non-Goals

Intelligent fuzzing is not:

- proof of correctness;
- a replacement for contract tests;
- a replacement for golden samples;
- unrestricted random corruption;
- production monitoring.

It is a discovery and hardening mechanism.

## Success Criteria

Intelligent fuzzing is effective when:

- it discovers bugs not covered by golden samples;
- it produces minimal reproducible cases;
- it classifies expected and unexpected failures cleanly;
- it explores valid-looking boundary cases;
- it strengthens FORML contracts over time;
- it can be integrated into CI without excessive noise.
