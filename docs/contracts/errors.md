# Error Boundaries Contract

> Status: P0 / Needs Stabilization  
> Scope: Error ownership across FORML layers  
> Implementation: Error classes exist, boundaries need cleanup  
> Audience: maintainers, testers, Miova campaign authors

## Purpose

The Error Boundaries contract defines where errors should be raised and how they should be classified.

It answers the question:

```text
Which layer owns this failure?
```

Clear error boundaries are essential for debugging, testing, user diagnostics and Miova expected failures.

---

## Error Ownership

| Boundary | Error Family | Example |
|---|---|---|
| Source → CST | Parser errors | invalid syntax |
| CST → AST | Builder errors | missing RHS, malformed node |
| AST → Semantic | Semantic errors | unbound variable, incompatible scope |
| Semantic → IR1 | IR translation errors | missing resolved binding |
| IR1 → IR2 | Normalization errors | unsupported logical shape |
| Model → Schema | Model errors | unsupported model format/framework |
| Schema → Semantic | Schema semantic errors | unknown feature |
| Aggregation | Aggregation errors | missing model constraints |
| Lowering | Lowering errors | unsafe minimization |
| IR → Backend | Backend compilation errors | unsupported solver feature |
| Runtime | Verification errors | backend execution failure |

---

## Required Error Properties

Errors should expose:

- layer/boundary;
- human-readable message;
- original artifact or node if safe;
- causal exception;
- diagnostic context;
- expected vs unexpected failure classification when used by Miova.

---

## Parser vs Semantic Errors

Parser errors must represent syntax failures only.

Semantic errors should not be wrapped as parser errors.

This distinction matters because:

- syntax failures are user source issues;
- semantic failures are meaning/model/context issues;
- Miova campaigns rely on expected failure stage;
- diagnostics become misleading if every error becomes a parser error.

---

## Current Stabilization Need

Current code contains parser and semantic error families, but the top-level validation path should avoid collapsing semantic exceptions into parser exceptions.

Target behavior:

```text
invalid syntax       → ParserError
invalid AST shape    → BuilderError or structural error
invalid semantics    → SemanticError / InvalidPropertyError
invalid model        → ModelError
invalid IR transform → IRError
invalid backend      → BackendError
```

---

## Expected vs Unexpected Failures

FORML should distinguish:

| Failure Type | Meaning |
|---|---|
| Expected failure | Invalid input rejected at the correct boundary. |
| Unexpected failure | Valid input rejected, invalid input accepted, or wrong boundary rejection. |
| Internal failure | Crash, assertion error, unclassified exception. |

Miova campaigns should use this distinction directly.

---

## Non-Goals

This contract does not define:

- the final user-facing CLI output format;
- localization;
- telemetry;
- full traceback rendering policy.

---

## Miova Hooks

Miova should assert that mutated artifacts fail at the expected boundary.

Examples:

| Mutation | Expected Boundary |
|---|---|
| broken syntax | parser |
| missing AST assertion | builder/semantic |
| unbound variable | semantic |
| invalid NNF shape | IR1/IR2 |
| missing model feature | schema-semantic |
| unsupported solver operator | backend boundary |
