# Architecture Decision Records

> Status: Active  
> Scope: Toetra architecture, compiler pipeline, verification pipeline, ModelBridge, Miova integration, and product identity

## Purpose

This section records the major architecture decisions behind Toetra.

Toetra is not only a collection of Python modules. It is a layered system that transforms a user-defined ML behavioral specification into progressively more formal verification artifacts.

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
- why specification constants use context-aware bare-name resolution,
- why points, lexical bindings and model evaluations are represented independently,
- why numeric semantics and backend compatibility are explicit verification contracts,
- why backend execution policy and termination evidence are backend-neutral,
- why verification provenance is content-addressed, portable and explicit about incomplete evidence,
- why CI, distributions and review bundles are verified release contracts,
- why the public V1 profile is narrow, executable and explicitly frozen,
- why model outputs are typed ports with declarative observables,
- why model-family semantic lowering is explicit and auditable,
- why the first binary-classification profile is deliberately constrained,
- why Toetra is the single canonical product, package and language identity,
- why installable code uses a `src`-based single-package layout,
- why public verification failures are normalized without erasing their
  owning internal boundary,
- why public repository exposure, the CLI contract, and the stable release are
  separate projects,
- and why public source access is noncommercial while commercial rights require
  a separate agreement.

## ADR format

Each ADR follows the same structure:

```text
Status
Context
Decision
Rationale
Consequences
Alternatives considered
Impact on Toetra
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
| ADR-0008 | Use ModelSchema as the bridge between models and Toetra |
| ADR-0009 | Introduce assertion aggregation before backend lowering |
| ADR-0010 | Use Z3 as the minimal V1 backend boundary |
| ADR-0011 | Preserve error boundaries between layers |
| ADR-0012 | Use Miova for mutation boundaries and contract validation |
| ADR-0013 | Use explicitly bound quantified variables |
| ADR-0014 | Represent comparisons as relations between scalar expressions |
| ADR-0015 | Preserve typed domains and lower them into provenanced assumptions |
| ADR-0016 | Use specification constants and context-aware bare-name resolution |
| ADR-0017 | Use first-class points, lexical bindings and point-indexed model evaluations |
| ADR-0018 | Make numeric semantics and framework/model/backend compatibility explicit |
| ADR-0019 | Define a backend-neutral execution contract |
| ADR-0020 | Make verification provenance content-addressed and portable |
| ADR-0021 | Treat release engineering as a verified product contract |
| ADR-0022 | Freeze the public V1 profile, compatibility policy and license |
| ADR-0023 | Represent model outputs as typed ports and declarative observables |
| ADR-0024 | Lower observables through explicit model-family semantics |
| ADR-0025 | Define the initial binary logistic classification profile |
| ADR-0026 | Extend the public V1 profile with binary classification |
| ADR-0027 | Adopt Toetra as the canonical product identity |
| ADR-0028 | Adopt a `src`-based single-package layout |
| ADR-0029 | Normalize public verification failures without erasing ownership |
| ADR-0030 | Separate public repository exposure, CLI, and stable release |
| ADR-0031 | Adopt noncommercial and separate commercial licensing |

## Decision status vocabulary

| Status | Meaning |
|---|---|
| Accepted | Decision is part of the current architecture |
| Stabilizing | Decision is accepted but implementation details may evolve |
| Planned | Decision is required by the target architecture but not implemented yet |
| Superseded | Decision has been replaced by a newer ADR |
