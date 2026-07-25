# Mutation Boundaries Contract

> Status: P0 / Planned / Critical  
> Scope: How Miova challenges FORML artifacts  
> Implementation: external Miova integration planned for FORML  
> Audience: Miova authors, FORML maintainers, test authors

## Purpose

The Mutation Boundaries contract defines where and how FORML artifacts may be mutated for validation campaigns.

It answers the question:

```text
What does it mean to challenge FORML safely and meaningfully?
```

Miova is not part of the normal FORML verification path. It is a testing and exploration layer used to validate compiler robustness.

---

## Mutation Philosophy

FORML should be tested as a sequence of artifacts.

Each artifact has:

- a layer;
- a contract;
- valid states;
- invalid states;
- expected failure boundaries;
- invariants.

Miova explores whether those contracts hold under controlled mutations.

---

## Official Mutation Layers

| Layer | Artifact | Example Mutation |
|---|---|---|
| Source | `.toetra` text | corrupt keyword, delete operator |
| CST | parser tree | remove subtree, reorder section |
| AST | `ProgramNode`, `PropertyNode` | delete scope, mutate assertion |
| Semantic | annotations/context | remove binding, corrupt symbol table |
| IR1 | `VerificationTask`, `LogicalIR` | inject invalid negation, mutate operator |
| IR2 | normal forms | break CNF/DNF invariant |
| ModelSchema | model representation | remove feature, change dtype |
| Aggregation | assertion set | remove constraint family |
| Lowering | lowered query | remove trace, unsafe simplification |
| BackendQuery | backend artifact | unsupported solver node |

---

## Expected Outcomes

Mutation outcomes should be classified as:

| Outcome | Meaning |
|---|---|
| Success | Mutation produced a valid artifact and pipeline continued. |
| Rejection | Mutation produced an invalid artifact rejected at the expected boundary. |
| Failure | Mutation triggered unexpected crash or wrong-layer error. |
| Skipped | Mutation was not applicable to the artifact. |

---

## Contract-Driven Mutation

A mutation should declare:

- intent;
- target layer;
- applicability condition;
- expected outcome;
- expected failure boundary;
- preservation expectations;
- severity.

This prevents mutation testing from becoming random corruption only.

---

## Invariants

Examples of invariants Miova can test:

| Invariant | Layer |
|---|---|
| valid source either parses or fails with parser error | Source |
| AST contains no raw Lark nodes | AST |
| semantic attributes are resolved before IR1 | Semantic |
| IR1 NNF has negations only above atoms | IR1 |
| IR2 CNF/DNF structure is valid | IR2 |
| ModelSchema features have dtype | ModelBridge |
| Aggregated assertions preserve origins | Aggregation |
| LoweredQuery preserves traceability | Lowering |

---

## Non-Goals

Miova integration must not:

- become required for normal user verification;
- hide compiler bugs;
- silently repair invalid artifacts;
- replace formal backend verification;
- mutate production artifacts without explicit campaign context.

---

## Relationship with FORML End-to-End Testing

Miova complements traditional test.

| Test Type | Purpose |
|---|---|
| Unit tests | Verify individual functions/classes. |
| Contract tests | Verify layer boundaries. |
| Golden tests | Verify stable end-to-end examples. |
| Miova campaigns | Explore robustness and failure boundaries. |

---

## Target Campaigns

Initial FORML Miova campaigns should include:

1. Source syntax mutation campaign.
2. AST structural mutation campaign.
3. Semantic binding mutation campaign.
4. IR1 logical mutation campaign.
5. ModelSchema mutation campaign.
6. AggregatedAssertionSet mutation campaign once implemented.
7. Backend boundary mutation campaign once backend queries exist.
