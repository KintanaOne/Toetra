# ADR-0020 — Make Verification Provenance Content-Addressed and Portable

- **Status:** Accepted
- **Date:** 2026-07-19
- **Scope:** runtime inputs, compiler configuration, backend routing and reporting

## Context

A verification result is useful only when a reviewer can identify what was verified and under which semantic and operational configuration it was produced. Filenames and timestamps are insufficient because artifacts can be renamed, overwritten or supplied in memory.

FORML must identify the specification, model or normalized schema, dataset and anchors when used, compiled property, selected route, execution policy and complete verification configuration. The design must remain framework-neutral and backend-neutral, and must never fabricate evidence for opaque external sources.

## Decision

FORML records content-addressed provenance for each `verify(...)` invocation and derives property-level provenance for every completed report.

### Artifact evidence

Every artifact records its role, source kind, fingerprint state, optional human-readable name, optional content fingerprint and an explanation when evidence is unavailable.

| State | Meaning |
|---|---|
| `AVAILABLE` | FORML computed a content fingerprint. |
| `UNAVAILABLE` | The artifact was used but could not be fingerprinted. |
| `NOT_PROVIDED` | The optional artifact was not supplied. |
| `NOT_USED` | The artifact category was not consumed. |

Provenance is `COMPLETE` only when every consumed artifact has auditable evidence. It is `PARTIAL` when at least one consumed artifact is `UNAVAILABLE`.

### Canonicalization

SHA-256 is the initial digest algorithm. The canonicalization method is explicit in every fingerprint.

| Input | Canonicalization |
|---|---|
| FORML source | exact UTF-8 compiler source |
| Serialized model or dataset | raw file bytes |
| Normalized `ModelSchema` | deterministic canonical JSON |
| In-memory pandas anchors | canonical JSON including columns, dtypes, index and records |
| Opaque custom resolver | unavailable until it exposes an auditable contract |

Human-readable filenames do not participate in content identity.

### Derived fingerprints

FORML records five independent identifiers:

1. **input fingerprint** — artifacts and compiler policy shared by the session;
2. **property fingerprint** — normalized property and actual IR2 form;
3. **route fingerprint** — backend profile and numeric compatibility route;
4. **execution-policy fingerprint** — timeout, resources, deterministic settings and backend options;
5. **verification fingerprint** — composition of the previous four identifiers.

Capture time is excluded so identical reruns retain the same verification identity.

### Software and compiler identity

Reports record the FORML version and optional build identifier, Python runtime, core component versions, requested and actual normal forms, distribution limit, fallback policy, backend hint, strictness and available IR builder metadata.

### Reporting contract

The JSON report schema becomes version 5. A property report contains all five fingerprints. A collection exposes only shared session evidence and never copies the first property's route or property identity into the collection envelope.

Text, HTML, records and DataFrames expose concise provenance identifiers and completeness.

## Security boundary

SHA-256 is an integrity identifier, not a signature, attestation, trusted timestamp or chain-of-custody proof. Signed attestations, registry-backed lineage and organizational governance remain platform concerns.

## Consequences

### Positive

- Results can be compared by exact inputs and configuration.
- Equal reruns keep stable identities after harmless file renames.
- Partial evidence is explicit.
- Framework, encoder and backend routes remain auditable without centering sklearn or Z3.
- Reports can later be indexed or signed without redesigning the core result model.

### Costs

- Hashing large artifacts adds startup I/O.
- Canonicalization formats become versioned contracts.
- External sources need dedicated adapters for complete provenance.
- Semantically equivalent but differently serialized models intentionally have different raw-artifact fingerprints.

## Alternatives considered

### Store paths and timestamps only

Rejected because paths are mutable and machine-specific.

### Hash only the model

Rejected because the specification, schema, data, anchors, route and policy all affect meaning.

### Hash a custom resolver's class name

Rejected because a class name does not identify the data returned.

### Include timestamps in fingerprints

Rejected because identical reruns would never share an identity.

### Add signatures in V1 Core

Deferred because signatures require key management and trust policy beyond portable local provenance.

## Patch 21 application

ADR-0024 extends provenance with model-semantic lowering evidence. Classification
reports must preserve both the declarative label/probability intention and the
canonical constraint executed by a backend; the latter must never replace the
former in content-addressed evidence.

## P21.9 additive report evidence

Binary-classification evidence is added to JSON v5 through the optional
`model_evaluations` field. Existing assignment, provenance, execution, and
numeric-compatibility fields retain their previous meaning. Each lowering trace
records semantic-profile and transformation versions, including the certified
probability-threshold transformation version introduced by P21.8.1.
