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
