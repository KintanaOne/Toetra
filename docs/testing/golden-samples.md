
# Golden Samples

> Status: Implemented and required
> Scope: Stable source examples and normalized expected artifacts

## Purpose

Golden samples are canonical Toetra cases that freeze observable behavior across layers.

They are the bridge between documentation and implementation.

## Required Artifact Bundle

A fully materialized sample may contain:

```text
<sample-id>/
├── source.toetra
├── metadata.yaml
├── cst.json
├── ast.json
├── semantic.json
├── ir1.json
├── ir2.json
├── verification-condition.json
├── backend-query.json
└── result.json
```

Only artifacts reached by the current implementation gate are mandatory. Missing later artifacts must be marked `planned`, not fabricated.

## Canonical Serialization Rules

Snapshots must:

- use stable enum values;
- preserve operand order;
- preserve source identifiers and provenance IDs;
- expose boundary kinds explicitly;
- serialize scalar trees recursively;
- avoid Python object addresses and unstable `repr` output;
- distinguish absent fields from null semantic values.

## Mandatory Valid Catalog

| ID | Purpose | Minimum layers |
|---|---|---|
| QV-001 | universal target bound with full domain syntax | parser → semantic |
| QV-002 | explicit quantified feature binding | parser → IR1 |
| QV-003 | implicit feature resolution | parser → IR1 |
| QE-001 | existential witness semantics | parser → aggregation |
| DOM-001 | all four interval boundary combinations | parser → IR2 |
| DOM-002 | numeric finite set | parser → backend |
| DOM-003 | symbolic finite set and capability requirement | parser → routing |
| ARI-001 | arithmetic precedence | parser → IR1 |
| ARI-002 | unary arithmetic | parser → IR1 |
| ARI-003 | arithmetic domain bounds | parser → IR2 |
| ARI-004 | initial affine profile | parser → backend |
| ARI-005 | nonlinear requirement classification | parser → routing |
| PW-001 | pointwise scope distinct from quantification | parser → semantic |
| SPC-001 | reusable business thresholds | parser → backend |
| SPC-002 | feature and constant share a name | parser → semantic |
| SPC-003 | constant-first resolution with implicit-feature fallback | parser → IR1 |
| SPC-004 | constant in numeric finite set | parser → IR2 |
| SPC-005 | one constant reused across properties | parser → aggregation |
| SPC-006 | string constant plus symbolic finite-set literal | parser → routing |

The source text and meaning of these IDs are defined in `docs/language/examples.md`.

## Mandatory Invalid and Unsupported Catalog

| ID family | Expected boundary |
|---|---|
| `SYN-*` | parser |
| `SEM-BIND-*` | semantic binding |
| `SEM-DOM-*` | semantic domain validation |
| `SEM-ARI-*` | semantic type/expression validation |
| `SEM-SPC-*` | specification-constant registration, resolution and typing |
| `UNSUP-*` | backend capability matching |

Definitions live in `docs/language/invalid-examples.md`.

## Metadata Example

```yaml
id: QV-001
status: valid
language_profile: quantified-domain-arithmetic-v1
quantifier: forall
expected_layers:
  parser: pass
  builder: pass
  semantic: pass
  ir1: pass
  ir2: pass
  backend: capability-dependent
requirements:
  categorical_values: true
  finite_set_membership: true
```

## Review Rule

A changed golden snapshot requires review as one of:

```text
intentional language change
intentional artifact-shape change
bug fix
unexpected regression
```

No bulk snapshot update should be accepted without identifying which category applies.

## Related Documents

- [Normative Examples](../language/examples.md)
- [Invalid Examples](../language/invalid-examples.md)
- [Language Evolution Test Matrix](language-evolution-test-matrix.md)
