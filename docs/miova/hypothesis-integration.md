# Hypothesis Integration

> Status: P0 — planned integration  
> Implementation: planned  
> Scope: combining Hypothesis strategies with Miova artifact mutation campaigns

## Purpose

This document defines how Hypothesis and Miova should work together in FORML.

Hypothesis is responsible for generating structured examples. Miova is responsible for mutating artifacts, applying contracts, checking invariants, and classifying mutation outcomes.

Together, they create a two-axis exploration strategy:

```text
Hypothesis explores the input space.
Miova explores the transformation and mutation space.
```

## Why Combine Them

FORML needs both approaches.

Hypothesis can generate many valid or invalid examples:

```text
valid DSL programs;
valid AST nodes;
valid logical trees;
valid ModelSchema objects;
invalid compatibility combinations.
```

Miova can then mutate the artifacts produced from those examples:

```text
source → AST → semantic AST → IR1 → IR2 → aggregated assertions
```

This makes it possible to test not only whether generated examples compile, but also whether the compiler remains robust when intermediate artifacts are challenged.

## Recommended Flow

```text
Hypothesis strategy
    ↓
generated FORML source or artifact
    ↓
normal FORML pipeline
    ↓
Miova artifact wrapping
    ↓
controlled mutation campaign
    ↓
contract and invariant checks
    ↓
classified result
```

## Example Campaign Pattern

```text
@given(valid_forml_source())
def test_generated_source_survives_expected_mutations(source):
    cst = parse(source)
    ast = build(cst)
    semantic_ast = validate(ast)
    ir1 = lower_to_ir1(semantic_ast)

    artifact = Artifact(kind="forml.ir1", payload=ir1)
    result = miova.apply(artifact, mutation="flip_comparison_operator")

    assert result.status in {SUCCESS, REJECTED, SKIPPED}
    assert result.status != FAILED
```

The exact API may evolve, but the principle should remain stable.

## Generated Seeds

Hypothesis can produce seeds for Miova campaigns:

| Seed | Miova target |
|---|---|
| valid source | source mutation campaign |
| parsed CST | CST mutation campaign |
| valid AST | AST mutation campaign |
| semantic AST | semantic mutation campaign |
| valid IR1 | IR mutation campaign |
| ModelSchema | schema mutation campaign |
| AggregatedAssertionSet | aggregation mutation campaign |

## Shrinking and Reproducibility

Hypothesis shrinking is especially valuable for Miova.

When a Miova mutation reveals a bug, the generated source or artifact should be shrunk to the smallest reproducible case.

This minimal case can then become:

- a regression test;
- a golden sample;
- a contract test;
- an ADR example if it reveals a design decision.

## Outcome Classification

The combined Hypothesis + Miova strategy should never treat all failures equally.

| Result | Meaning |
|---|---|
| `SUCCESS` | mutation produced an accepted valid artifact |
| `SKIPPED` | mutation was not applicable to the generated case |
| `REJECTED` | mutation violated a known contract or invariant |
| `FAILED` | unexpected crash or unclassified behavior |

Only `FAILED` should be considered a testing failure by default.

Some campaigns may also assert expected rejection rates or layer-specific rejection boundaries.

## Non-Goals

This integration does not mean that Miova becomes Hypothesis.

Hypothesis remains a generation and shrinking tool. Miova remains a mutation, contract, invariant, and campaign orchestration framework.

## Success Criteria

The integration is successful when:

- Hypothesis can generate meaningful FORML seeds;
- Miova can mutate those seeds at several layers;
- expected failures are classified precisely;
- unexpected failures shrink to readable examples;
- new bugs become regression tests;
- the combined system improves confidence in compiler evolution.
