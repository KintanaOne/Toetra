# Numeric Compatibility Reporting Contract

> Status: Implemented by Patch 16.3  
> Scope: compatibility assessment → user-facing report → generated matrices  
> Architectural constraint: framework-neutral and backend-neutral

## Purpose

A backend status is not sufficient to state what has been proved about a source
model. Every compatibility-aware verification report must preserve the route
that justified execution and the semantic boundary that limits the conclusion.

```text
framework/model descriptor
+ model encoder descriptor
+ backend numeric profile
+ property numeric requirements
→ matched compatibility rule
→ interpreted backend conclusion
→ text / JSON / HTML report
```

The reporting layer must never infer compatibility from a backend name such as
`Z3`, or from a framework name such as `sklearn`.

## Required report fields

When a numeric compatibility assessment exists, the public report records:

- matched rule identifier;
- implementation support status;
- semantic compatibility classification;
- named semantic target;
- conclusion scope;
- evidence identifier;
- framework adapter, version, model family and source execution profile;
- ModelBridge encoder identifier and version;
- backend kind, adapter, version and numeric profile;
- property-level numeric requirements;
- permitted conclusion kinds;
- conclusions requiring concrete replay;
- assumptions and preconditions;
- compatibility diagnostics;
- documentation reference.

This information is normalized into `ReportNumericCompatibility`. Renderers
consume that backend-neutral object and do not inspect solver-native metadata.

## Semantic-boundary rule

A result with:

```text
classification = LOSSY
conclusion_scope = SEMANTIC_TARGET_ONLY
```

may remain `PROVED`, `COUNTEREXAMPLE`, `WITNESS` or `NO_WITNESS` only for its
explicitly named semantic target. The public summary must say that the result
does not automatically apply to concrete source execution.

For source-artifact conclusions:

| Classification | Sound conclusion directions |
|---|---|
| `EXACT` | all four logical conclusion kinds |
| `SOUND_OVER_APPROXIMATION` | universal proof and existential no-witness |
| `SOUND_UNDER_APPROXIMATION` | universal counterexample and existential witness |
| `LOSSY`, `INCOMPATIBLE`, `UNKNOWN` | none without a narrower semantic target |

Any backend conclusion outside the rule's permitted set is downgraded to
`UNKNOWN` before reporting.

## JSON contract

Patch 16.3 introduced the `numeric_compatibility` field in schema version 3.
The current Toetra report schema is version 6 and contains a top-level
`numeric_compatibility` object, or `null` only for legacy/manual executions that
do not use compatibility-aware routing.

```json
{
  "schema": "toetra.verification-report",
  "schema_version": 6,
  "numeric_compatibility": {
    "rule_id": "...",
    "support_status": "supported",
    "classification": "lossy",
    "semantic_target": "toetra.real_affine_extracted_model",
    "conclusion_scope": "semantic_target_only",
    "source": {},
    "model_encoder": {},
    "backend": {}
  }
}
```

Patch 18 may add session provenance such as artifact fingerprints and component
versions. It must extend this compatibility object rather than reconstructing
numeric meaning from those fingerprints.

## Generated matrices

The normative registry generates two independent public views:

1. a support matrix describing implemented framework/model/encoder/backend
   combinations;
2. a semantic guarantee matrix describing classification, target, conclusion
   scope and permitted conclusions.

The checked-in page is:

```text
docs/generated/numeric-compatibility-matrices.md
```

Generate it with:

```bash
python scripts/docs/generate_numeric_compatibility_matrices.py
```

Check that it is current without modifying files:

```bash
python scripts/docs/generate_numeric_compatibility_matrices.py --check
```

A unit test performs the same equality check. Manual edits to generated tables
are contract failures.

## Tests required for every new route

A new compatibility rule must exercise:

- deterministic matrix generation;
- exact route serialization;
- text and HTML visibility of semantic target and conclusion scope;
- every permitted and forbidden conclusion direction;
- a representative boundary where source execution and encoded semantics may
  diverge;
- fail-closed behavior for unmatched or incompatible routes.
