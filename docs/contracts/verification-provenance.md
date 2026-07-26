# Verification Provenance Contract

> Status: Implemented
> Source of truth: `toetra._provenance`
> Report schema: `toetra.verification-report` version 6

## Purpose

The contract identifies the exact inputs and configuration behind a result, states whether evidence is complete, and allows reports representing the same verification task to be compared.

```text
invocation artifacts + compiler policy
→ VerificationProvenanceContext

context + property IR2 + route + execution policy
→ ReportProvenance
```

## Artifact contract

Each `ArtifactProvenance` contains a role, source kind, state, optional name, optional `ContentFingerprint` and an unavailability reason.

| State | Fingerprint | Reason |
|---|---:|---:|
| `available` | required | optional |
| `unavailable` | forbidden | required |
| `not_provided` | forbidden | optional |
| `not_used` | forbidden | optional |

Only an unavailable artifact that was actually consumed makes provenance `partial`. Presentation names are excluded from content identity.

## Canonical fingerprints

A content fingerprint records algorithm, digest, canonical byte size and canonicalization identifier.

| Artifact | Identifier |
|---|---|
| Specification source | `utf8_compiler_source` |
| File model, dataset or anchors | `raw_file_bytes` |
| Model schema | `toetra_model_schema_canonical_json_v3` |
| pandas anchors | `pandas_dataframe_canonical_json_v1` |

Canonical JSON preserves deterministic mapping order, sequence order, type distinctions and exact floating-point identity. Unsupported opaque values fail closed rather than using unstable `repr(...)` output.

## Fingerprint hierarchy

- **Input** covers artifacts and compiler policy.
- **Property** covers property type, semantics, scope, normal form and normalized formula.
- **Route** covers backend profile and numeric compatibility evidence.
- **Execution policy** covers timeout, work and memory budgets, deterministic seed and options.
- **Verification** composes the four preceding identifiers.

Timestamps and human-readable names are excluded from these identities.

## Runtime access

```python
session.provenance.input_fingerprint
session.provenance.completeness

report.provenance.verification_fingerprint
report.provenance.route_fingerprint
report.provenance.artifacts["model"]
```

Records and DataFrames add `verification_fingerprint`, `input_fingerprint` and `captured_at_utc`.

## JSON v6

```json
{
  "provenance": {
    "captured_at_utc": "2026-07-19T12:00:00Z",
    "completeness": "complete",
    "fingerprints": {
      "inputs": "sha256:...",
      "property": "sha256:...",
      "route": "sha256:...",
      "execution_policy": "sha256:...",
      "verification": "sha256:..."
    },
    "artifacts": {},
    "software": {
      "toetra_version": "1.0.0rc3",
      "toetra_build_id": "git:..."
    },
    "compiler": {}
  }
}
```

Collections expose only shared input/session evidence. Property and route identities remain on individual reports.

## Completeness examples

| Scenario | Completeness |
|---|---|
| Serialized model and dataset fingerprinted | complete |
| Schema-only verification | complete |
| In-memory pandas anchors canonicalized | complete |
| Opaque custom anchor resolver | partial |
| Optional dataset not used | complete |

## Adapter requirement

An external source adapter may claim complete provenance only when it supplies immutable canonical evidence for the exact content consumed. A URL, class name or logical identifier alone is insufficient.

## Security limit

Core provenance does not provide signatures, trusted timestamps, chain of custody, remote immutability, authorization or organizational audit policy.

## Test obligations

Tests must preserve deterministic content identity, exact float distinctions, rename invariance, change sensitivity, fail-closed opaque values, collection/property separation and consistent text, JSON, HTML and DataFrame output.
