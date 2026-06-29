# Dependencies

> Status: Stabilizing  
> Scope: Architecture dependency map  
> Implementation: Partially implemented  
> V1 backend scope: Z3 only

## Purpose

This document maps the conceptual and technical dependencies of FORML.

It answers four questions:

1. Which dependencies are required for the first functional V1?
2. Which dependencies are optional development tools?
3. Which dependencies belong to future or post-V1 extensions?
4. Which dependencies are external systems rather than part of FORML itself?

Dependency classification matters because FORML is intended to remain modular. The first end-to-end path should be achievable without requiring every future backend, runtime, or orchestration capability to exist.

---

## Dependency categories

FORML dependencies are classified into five categories.

| Category | Meaning |
|---|---|
| Core V1 | Required to run the minimal end-to-end path. |
| Stabilizing | Already present or partially present, but still being hardened. |
| Development | Used for tests, docs, validation, or local development. |
| Optional | Useful when a feature or framework is available, but not mandatory. |
| Post-V1 | Explicitly outside the first functional V1. |

---

## Core V1 dependencies

The first functional FORML V1 should require only the components needed for a Z3-backed end-to-end verification path.

| Dependency | Role | Status |
|---|---|---|
| Python | Main implementation language. | Core V1 |
| Lark | Parses `.forml` source into a CST. | Core V1 |
| Z3 / z3-solver | Minimal verification backend for V1. | Core V1 |
| dataclasses / typing | Core data structures for AST, IR, schemas, and contracts. | Core V1 |

The V1 dependency target is intentionally narrow. FORML should not require ERAN, PyTorch, TensorFlow, or advanced verification engines to prove the first end-to-end path.

---

## Compiler dependencies

The compiler pipeline depends on a strict chain of internal artifacts.

```text
.forml source
→ CST
→ AST
→ SemanticValidatedAST
→ IR1-NNF
→ IR2-CNF/DNF
→ AggregatedAssertionSet
→ LoweredQuery
→ BackendQuery
```

| Internal dependency | Depends on | Produces |
|---|---|---|
| Parser | Grammar | CST |
| Builder | CST + AST node definitions | AST |
| Semantic Validator | AST + semantic rules | SemanticValidatedAST |
| IR1 Translator | SemanticValidatedAST | IR1 verification tasks |
| IR2 Normalizer | IR1 | CNF/DNF-oriented logical forms |
| Assertion Aggregator | IR2 + semantic/model constraints | AggregatedAssertionSet |
| Lowering / Minimization | Aggregated assertions + backend capabilities | LoweredQuery |
| Backend Boundary | LoweredQuery + backend target | BackendQuery |

---

## ModelBridge dependencies

ModelBridge is responsible for model loading, framework detection, introspection, and schema production.

| Dependency | Role | Status |
|---|---|---|
| joblib | Load `.joblib` serialized models. | Stabilizing |
| pickle | Load `.pkl` serialized models. | Stabilizing |
| pandas | Infer feature schema from datasets. | Stabilizing |
| scikit-learn | Supported model family for V1-oriented schema extraction. | Stabilizing |
| XGBoost | Optional model family through sklearn-compatible introspection. | Optional |
| PyTorch | Future model framework. | Post-V1 |
| TensorFlow | Future model framework. | Post-V1 |

ModelBridge must not force all ML frameworks to be installed. Optional framework support should remain guarded by optional imports or extras.

---

## Backend dependencies

Z3 is the minimal backend for the first functional V1.

| Backend | Role | Status |
|---|---|---|
| Z3 | Minimal symbolic verification backend. | Core V1 |
| ERAN | Neural network robustness verification backend. | Post-V1 |
| Zonotope / Box abstractions | Abstract interpretation strategies. | Post-V1 |
| Additional solvers | Future backend expansion. | Post-V1 |

The V1 architecture should therefore optimize for a clean `BackendQuery → Z3` path before generalizing to multi-backend orchestration.

---

## Testing dependencies

| Dependency | Role | Status |
|---|---|---|
| pytest | Unit, contract, regression and integration testing. | Development |
| Hypothesis | Property-based generation for DSL, AST, IR, and edge cases. | Development |
| Miova | Mutation campaigns, artifact boundary testing, invariant testing. | Development / external integration |
| MkDocs | Documentation site generation. | Development |
| Mermaid | Architecture diagrams in documentation. | Development |

Hypothesis and Miova serve different purposes. Hypothesis generates structured examples; Miova mutates typed artifacts across pipeline boundaries.

---

## External systems

These are not FORML internals.

| External system | Relationship to FORML |
|---|---|
| User ML model | Input artifact consumed through ModelBridge. |
| Dataset / schema | Source of feature metadata and type information. |
| Z3 solver | First backend execution engine. |
| CI system | Future execution environment for FORML checks. |
| Miova package | External mutation framework integrated for robustness testing. |

---

## V1 dependency rule

The first V1 should remain minimal:

```text
FORML V1 = DSL compiler + ModelBridge schema + IR pipeline + Z3 backend query + verification result
```

Everything else should be documented as extension, not as a prerequisite.

---

## Design implications

FORML dependency design should follow these rules:

1. Keep the compiler independent from optional ML frameworks.
2. Keep ModelBridge framework support optional when possible.
3. Keep the Z3 path simple and first-class.
4. Keep multi-backend orchestration out of the critical V1 path.
5. Keep Miova as an external testing and mutation layer, not as a runtime dependency.

---

## Related documents

- `architecture/overview.md`
- `architecture/runtime-flow.md`
- `architecture/c4-container.md`
- `model-bridge/overview.md`
- `backends/z3.md`
- `contracts/ir-to-backend.md`
- `testing/property-based-testing.md`
- `miova/overview.md`
