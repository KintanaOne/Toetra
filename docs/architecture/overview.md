# FORML Architecture Overview

## Introduction

FORML is a formal verification and behavioral specification platform designed to bridge the gap between user-defined behavioral properties and backend-specific verification systems.

The project combines:

* Domain Specific Language (DSL) engineering
* Formal methods
* Logical transformations
* Multi-backend verification orchestration
* Runtime monitoring and behavioral validation

FORML is not limited to being a DSL compiler. It acts as a semantic orchestration layer capable of:

* understanding user verification intent,
* formally representing backend systems,
* selecting appropriate verification strategies,
* compiling backend-aware verification pipelines,
* and monitoring behavioral guarantees at runtime.

---

# High-Level System Overview

At a macro level, FORML is composed of four major subsystems:

1. User DSL Pipeline
2. Backend Representation Pipeline
3. Backend Orchestration System
4. Verification & Monitoring Runtime

```mermaid
flowchart LR

    U[User]
        --> D[.forml Specification]

    D
        --> P[DSL Compilation Pipeline]

    P
        --> O[Backend Orchestration]

    O
        --> V[Verification Runtime]

    V
        --> M[Monitoring & Observation]
```

---

# Core Architectural Philosophy

FORML is designed around progressive formalization.

Each pipeline stage transforms an object from a less constrained representation into a more formally validated and semantically precise representation.

The architecture follows several core principles:

* Explicit transformation stages
* Layer isolation
* Progressive validation
* Semantic preservation
* Backend-agnostic orchestration
* Formal intermediate representations
* Runtime observability

---

# Architectural Layers

## 1. DSL Compilation Pipeline

The DSL pipeline transforms a `.forml` specification into normalized formal representations.

This pipeline is responsible for:

* parsing,
* syntax validation,
* semantic validation,
* logical lowering,
* rewriting,
* normalization.

### Main stages

```text
.forml
→ CST
→ AST
→ Validated AST
→ IR Level 1
→ IR Level 2
→ Normalized Forms
```

The compilation pipeline guarantees that semantic meaning is preserved throughout transformations.

---

## 2. Backend Representation Pipeline

FORML must understand the target system it verifies.

The backend representation pipeline detects and transcribes backend-specific models into validated formal representations.

This subsystem allows FORML to:

* reason about backend capabilities,
* map logical properties to runtime entities,
* perform backend-aware verification,
* support multiple verification targets.

Examples of future backend targets may include:

* machine learning models,
* symbolic systems,
* runtime environments,
* verification engines,
* monitoring infrastructures.

---

## 3. Backend Orchestration System

FORML is backend-agnostic.

A verification backend may:

* be explicitly specified by the user,
* be selected automatically,
* or be dynamically chosen according to property constraints and backend capabilities.

This orchestration layer is responsible for:

* property analysis,
* capability matching,
* backend routing,
* compilation strategy selection,
* compatibility diagnostics.

This subsystem forms the foundation of the future AutoFORML system.

---

## 4. Verification & Monitoring Runtime

Once a backend strategy is selected, FORML compiles verification artifacts and executes runtime verification pipelines.

This subsystem is responsible for:

* verification execution,
* runtime monitoring,
* behavioral observation,
* trace collection,
* runtime diagnostics.

---

# Intermediate Representations (IR)

FORML uses multiple intermediate representations to progressively formalize user intent.

## IR Level 1

IR Level 1 represents the first backend-independent logical representation produced after semantic validation.

Its primary purpose is to:

* capture formal semantics,
* detach logic from DSL syntax,
* provide a stable transformation foundation.

---

## IR Level 2

IR Level 2 is dedicated to:

* normalization,
* rewriting,
* optimization,
* canonicalization,
* backend-aware transformation preparation.

This representation serves as the basis for formal rewriting systems such as:

* NNF,
* CNF,
* DNF,
* and future logical transformation passes.

---

# Validation Philosophy

Validation is a first-class architectural concern in FORML.

Each layer may introduce its own validation stage.

Examples include:

| Layer                  | Validation Type                |
| ---------------------- | ------------------------------ |
| Parsing                | Syntax validation              |
| AST                    | Structural validation          |
| Semantic Layer         | Type and symbol validation     |
| IR Layers              | Logical consistency validation |
| Backend Representation | Backend capability validation  |
| Runtime                | Behavioral verification        |

The objective is to progressively increase confidence guarantees across the pipeline.

---

# Semantic Preservation

One of the central architectural invariants of FORML is semantic preservation.

All transformation stages must preserve the logical meaning of the original user specification.

This includes:

* logical rewriting,
* normalization,
* backend lowering,
* optimization passes.

Semantic equivalence is considered a critical system invariant.

---

# Backend-Agnostic Design

FORML is intentionally designed to be backend-agnostic.

The system separates:

* user intent,
* logical semantics,
* backend representation,
* runtime verification strategy.

This separation allows:

* extensibility,
* multi-backend support,
* backend specialization,
* dynamic backend routing,
* automatic strategy selection.

---

# Future Directions

The architecture is intentionally designed to support future extensions such as:

* AutoFORML backend selection,
* capability scoring systems,
* advanced runtime instrumentation,
* distributed verification,
* temporal logic extensions,
* model checking integrations,
* formal proof generation,
* explainability systems,
* verification optimization strategies.

---

# Documentation Structure

The architecture documentation is organized into several dedicated sections.

```text
architecture/
├── overview.md
├── pipeline.md
├── layers/
│   ├── parsing.md
│   ├── ast.md
│   ├── semantic.md
│   ├── logic_ir.md
│   ├── nnf.md
│   ├── cnf.md
│   ├── dnf.md
│   ├── execution_plan.md
│   └── backend.md
```

Each document focuses on a specific architectural concern and defines:

* responsibilities,
* invariants,
* guarantees,
* transformation rules,
* validation constraints,
* and interactions with adjacent layers.

---

# Conclusion

FORML aims to provide a unified formal infrastructure capable of connecting:

* user behavioral intent,
* formal logical reasoning,
* backend-aware verification,
* and runtime behavioral monitoring.

The architecture emphasizes:

* modularity,
* formal correctness,
* extensibility,
* observability,
* and semantic rigor.

This documentation serves as the foundation for stabilizing and evolving the FORML ecosystem.
