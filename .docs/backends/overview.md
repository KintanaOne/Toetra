# Backends Overview

> Status: Planned / architecturally required  
> Scope: Backend architecture, verification strategy, backend boundary  
> Priority: P1

## Purpose

The backend layer is responsible for executing or delegating the verification problem produced by FORML.

FORML does not treat backends as syntax-level targets. A backend must receive a stable, explicit, backend-specific representation produced after semantic validation, logical normalization, assertion aggregation, model constraint integration, and lowering.

The backend layer answers the question:

```text
How is a validated FORML verification problem executed by a concrete verification engine?
```

## Position in the FORML pipeline

The backend layer sits after the logical verification pipeline:

```text
.forml source
→ CST
→ AST
→ SemanticValidatedAST
→ IR1 / NNF
→ IR2 / CNF-DNF
→ AggregatedAssertionSet
→ LoweredQuery
→ BackendQuery
→ VerificationBackend
→ VerificationResult
```

Backends should not consume:

- raw `.forml` source;
- CST nodes;
- AST nodes;
- semantic annotations directly;
- framework-specific model objects directly.

Backends should consume:

- a `BackendQuery`;
- backend-specific configuration;
- model constraints or symbolic model encodings;
- execution options;
- diagnostic context.

## Core responsibilities

The backend subsystem is responsible for:

| Responsibility | Description |
|---|---|
| Capability declaration | Describe what a backend can verify. |
| Compatibility checking | Reject unsupported property/model/query combinations early. |
| Backend query encoding | Convert lowered FORML queries into backend-native artifacts. |
| Execution | Run the verification query when the backend is executable. |
| Result normalization | Convert backend-native results into FORML `VerificationResult`. |
| Diagnostics | Explain unsupported features, solver failures, timeout, or inconclusive results. |

## Backend categories

FORML may eventually support several backend categories.

| Category | Examples | Role |
|---|---|---|
| SMT / symbolic solver | Z3 | Logical satisfiability, counterexamples, symbolic constraints. |
| Neural verification | ERAN, VeriNet-like systems | Robustness and neural-network-specific guarantees. |
| Abstract interpretation | Zonotope, box abstractions | Approximate robustness or bounds. |
| Runtime checker | Future FORML runtime | Runtime behavioral monitoring. |
| Diagnostic backend | Internal analyzers | Explainability, capability checking, early stops. |

## Current implementation status

The DSL already supports backend syntax such as `using z3`, `using ERAN`, `using box`, and `using zonotope` in the grammar and vocabulary.

However, backend execution is not yet the primary implemented layer. The current implementation focus is:

1. compiler pipeline;
2. semantic validation;
3. IR1 generation;
4. ModelBridge;
5. contracts and mutation/testing boundaries.

Backend support should therefore be documented as a **target architecture** until backend query generation and execution are implemented.

## Design principle

FORML should keep a strict separation between:

```text
User intent
Logical representation
Model representation
Backend query encoding
Backend execution
```

This separation prevents backend-specific assumptions from leaking into the language, AST, semantic layer, or IR1.

## Expected backend artifacts

A mature backend layer should introduce or stabilize artifacts such as:

```text
BackendCapability
BackendConfig
BackendQuery
BackendCompiler
BackendExecutionContext
VerificationResult
VerificationDiagnostic
```

These artifacts should be explicit, serializable when possible, and testable through contracts.

## Relationship with ModelBridge

ModelBridge does not execute verification. It provides the normalized model representation required for semantic validation and future model constraint generation.

The backend layer consumes model-derived constraints or symbolic model encodings, not raw model objects.

```text
ModelBridge
→ ModelSchema
→ ModelConstraintIR
→ AggregatedAssertionSet
→ LoweredQuery
→ BackendQuery
```

## Relationship with Miova

Miova should challenge backend boundaries by mutating:

- backend selection;
- backend configuration;
- lowered queries;
- backend queries;
- capability declarations;
- expected backend failures.

Miova should not be part of the normal verification runtime path. It is a validation and robustness layer for FORML artifacts.

## Non-goals

The backend layer is not responsible for:

- parsing FORML source;
- resolving DSL symbols;
- inferring model schemas;
- deciding semantic validity of properties;
- performing IR1 or IR2 normalization;
- mutating artifacts for test.

