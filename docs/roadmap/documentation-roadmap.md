# Documentation Roadmap

> Status: Active  
> Scope: Documentation planning

## Purpose

This roadmap tracks the FORML documentation structure and rewrite strategy.

FORML documentation is organized around:

- architecture,
- compiler layers,
- ModelBridge,
- IR,
- contracts,
- testing,
- Miova integration,
- runtime,
- backends,
- ADRs,
- roadmap.

## Documentation principle

Each document should answer four questions:

```text
What does this layer do?
Why does it exist?
What does it guarantee?
How is it tested or validated?
```

## Documentation maturity levels

| Level | Meaning |
|---|---|
| Draft | First version, may evolve |
| Stabilizing | Aligned with implementation direction |
| Contract | Defines expected behavior |
| Reference | Stable enough to guide implementation |
| Post-V1 | Future direction only |

## P0 documents

P0 documents define the architecture and contracts required for V1.

They include:

- `index.md`
- `docs-roadmap.md`
- architecture overview,
- pipeline views,
- runtime flow,
- status matrix,
- compiler pipeline,
- ModelBridge overview,
- IR overview,
- contracts,
- Miova integration,
- testing strategy,
- ADR overview.

## P1 documents

P1 documents improve external readability and extension planning.

They include:

- language reference,
- backend docs,
- runtime docs,
- C4 views,
- detailed ADRs.

## P2 documents

P2 documents improve onboarding and project communication.

They include:

- getting started,
- installation,
- first property,
- first model schema,
- end-to-end preview,
- implementation roadmap,
- open questions.

## Rewrite strategy

The documentation should be rewritten progressively in this order:

```text
1. Root docs
2. Architecture
3. Compiler
4. ModelBridge
5. IR
6. Contracts
7. Miova Integration
8. Testing
9. Language
10. Backends
11. Runtime
12. C4 views
13. ADRs
14. Getting Started
15. Roadmap
```

## Quality checklist

Each page should define:

- status,
- scope,
- current implementation status,
- target architecture,
- responsibilities,
- inputs and outputs,
- guarantees,
- non-goals,
- relation to tests,
- relation to Miova if relevant.

## Final consolidation

After all packs are integrated, the documentation should be checked for:

- broken links,
- duplicated concepts,
- inconsistent status labels,
- Z3 vs post-V1 backend wording,
- Miova runtime confusion,
- IR1 vs IR2 ambiguity,
- ModelBridge terminology,
- outdated SMS terminology,
- missing golden samples.

---

## Language Evolution Documentation Freeze

The documentation-first package is complete when patches 01 through 06 are applied:

```text
01 explicit quantified bindings
02 typed domains
03 arithmetic expressions
04 architecture decisions
05 cross-layer contracts
06 normative examples and test matrix
```

The next work belongs to implementation and test delivery, not additional speculative language documentation. Documentation should now evolve alongside concrete code changes and discovered edge cases.

## Patch 21 Classification Specification Freeze

P21.0 applies the same documentation-first rule to binary classification:

```text
01 typed output and observable ADR
02 model-semantic lowering ADR
03 initial binary-classification profile ADR
04 boundary contracts and amendments
05 declarative language reference
06 stable acceptance-test matrix
07 implementation roadmap with explicit debts
```

The accepted documents are implementation specifications, not retrospective
descriptions. Classification must not be added to the current public V1 profile
until the P21.11 release gate is complete.
