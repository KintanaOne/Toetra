# Architecture Decision Records

> Status: Active  
> Scope: FORML architecture, compiler pipeline, verification pipeline, ModelBridge, and Miova integration

## Purpose

This section records the major architecture decisions behind FORML.

FORML is not only a collection of Python modules. It is a layered system that transforms a user-defined ML behavioral specification into progressively more formal verification artifacts.

The goal of the ADR section is to make explicit:

- why the system is layered,
- why each artifact boundary exists,
- why semantic validation is separated from syntax construction,
- why IR1 and IR2 are distinct,
- why ModelBridge exists as a dedicated subsystem,
- why Z3 is the minimal V1 backend,
- why Miova is used as an external mutation and contract validation framework,
- why quantified variables are explicitly bound,
- why comparisons relate general scalar expressions,
- why typed domains are lowered into provenanced assumptions,
- and why specification constants use context-aware bare-name resolution.

## ADR format

Each ADR follows the same structure:

```text
Status
Context
Decision
Rationale
Consequences
Alternatives considered
Impact on FORML
```

## Current ADR list

| ADR | Decision |
|---|---|
| ADR-0001 | Use a staged compiler pipeline |
| ADR-0002 | Treat each compiler layer as a distinct artifact |
| ADR-0003 | Separate raw AST from semantically validated AST |
| ADR-0004 | Normalize enums and vocabulary at explicit boundaries |
| ADR-0005 | Use semantic annotations as runtime semantic cache |
| ADR-0006 | Define IR1 as NNF-oriented logical representation |
| ADR-0007 | Define IR2 as CNF/DNF normal-form layer |
| ADR-0008 | Use ModelSchema as the bridge between models and FORML |
| ADR-0009 | Introduce assertion aggregation before backend lowering |
| ADR-0010 | Use Z3 as the minimal V1 backend boundary |
| ADR-0011 | Preserve error boundaries between layers |
| ADR-0012 | Use Miova for mutation boundaries and contract validation |
| ADR-0013 | Use explicitly bound quantified variables |
| ADR-0014 | Represent comparisons as relations between scalar expressions |
| ADR-0015 | Preserve typed domains and lower them into provenanced assumptions |
| ADR-0016 | Use specification constants and context-aware bare-name resolution |

## Decision status vocabulary

| Status | Meaning |
|---|---|
| Accepted | Decision is part of the current architecture |
| Stabilizing | Decision is accepted but implementation details may evolve |
| Planned | Decision is required by the target architecture but not implemented yet |
| Superseded | Decision has been replaced by a newer ADR |
