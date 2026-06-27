# FORML Documentation

## Overview

FORML is a formalized framework for program representation, transformation, and verification.
It is designed to enable structured reasoning over programs, from high-level DSL constructs down to executable intermediate representations.

At its core, FORML is not only a language — it is a system for **controlling program evolution through structured transformations and verifiable constraints**.

---

## Core Philosophy

FORML is built around three fundamental principles:

### 1. Structured Program Representation

Programs are not treated as raw text but as structured artifacts that evolve through well-defined layers (CST, AST, IR).

### 2. Controlled Transformation

Program evolution is not implicit. It is explicitly defined through transformations governed by rules, contracts, and invariants.

### 3. Verifiable Semantics

Every transformation can be validated through formal or semi-formal properties, enabling debugging, fuzzing, and correctness reasoning.

---

## System Architecture

FORML is composed of several interconnected subsystems:

### 🔷 Core Pipeline

Responsible for parsing, representation, and multi-layer program transformation.

* DSL Parser
* CST / AST construction
* IR generation (multi-level)

---

### 🔷 SMS (Stable Mutations System)

SMS is the transformation and verification engine of FORML.

It defines:

* **Artifact Model** → structured program state
* **Transformation Model** → state transitions
* **Contract Model** → intent and expected behavior
* **Invariant Model** → verifiable truth constraints
* **Engine Model** → execution and orchestration
* **Registry Model** → transformation discovery system

SMS enables controlled mutation, fuzzing, and property-based validation of programs.

👉 [See SMS Documentation](./sms/sms_v1_architecture_spec.md)

---

## Use Cases

FORML is designed for:

* Program analysis and transformation
* DSL execution and verification
* Formal property testing (PBT / fuzzing)
* Research in structured program mutation
* Future integration with LLM-guided program synthesis

---

## Documentation Structure

* **FORML Core**

  * Language specification
  * Pipeline architecture
  * IR design

* **SMS System**

  * Architecture specification
  * Models (Artifact, Transformation, Contract, Invariant)
  * Execution semantics
  * ADRs and design decisions

---

## Getting Started

This documentation is organized to support progressive understanding:

1. Start with this overview
2. Explore the FORML pipeline
3. Dive into SMS architecture
4. Study individual models
5. Review ADRs for design rationale

---

## Status

FORML is an evolving system under active design.
SMS v1 represents the current stabilized architecture for transformation and verification.

---

## Navigation

* FORML Overview
* Pipeline & IR
* SMS Architecture
* Models
* ADRs
