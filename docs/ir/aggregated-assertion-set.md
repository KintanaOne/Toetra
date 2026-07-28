# IR2 assumptions and verification condition

> **Status:** Implemented
>
> **Filename note:** retained for stable links from earlier design documents

The current implementation represents the complete verification problem inside
`VerificationTaskIR2`. It does not define a class named
`AggregatedAssertionSet`.

## Task fields

| Field | Purpose |
|---|---|
| `spec_formula` | normalized public property `P` |
| `assumptions` | typed and traceable assumptions `Γ` |
| `verification_condition` | executable `Γ ∧ ¬P` or `Γ ∧ P` |
| `semantics` | universal refutation or existential witness |
| `normal_form` | actual NNF/CNF/DNF representation |
| `requirements` | capabilities required from a backend |
| `diagnostics` | structural/guardrail evidence |
| `lowering_evidence` | trace from public observable to canonical constraint |

## Assumption sources

`AssumptionIR2` carries a source, NNF formula, description, and metadata.
Implemented producers include:

- domain assumption encoder;
- anchor assumption encoder;
- model encoder;
- explicit internal caller assumptions.

Assumptions are preserved independently even though the executable condition
contains their conjunction.

## Model equations

For each requested model evaluation, the selected encoder contributes a model
assumption. The equation uses the exact point identity, feature order, output
port, coefficients, and intercept required by the schema.

Regression encodes the scalar affine output. Direct binary logistic regression
encodes the oriented decision quantity used by the semantic profile.

## Consistency

An inconsistent assumption set makes the admissible domain empty. The Z3 runner
can translate `task.assumptions` alone to distinguish that condition from an
ordinary absence of counterexample or witness. This diagnostic remains subject
to the total execution budget.

## Capability effect

Assumptions contribute to `IR2Requirements`. A model equation can require affine
arithmetic and model-assumption support; a domain can require ordered numeric
comparisons or finite-set support.

Backend capabilities are not logical assumptions. An unsupported capability
causes routing failure.

## Traceability

The task retains enough separation to report:

- assumption count and sources;
- point/output identity;
- original source property;
- canonical lowering;
- model-evaluation evidence;
- route and provenance fingerprints.

## Related documents

- [Compiler assumption composition](../compiler/assertion-aggregation.md)
- [IR1 to IR2 contract](../contracts/ir1-to-ir2.md)
- [Model constraints contract](../contracts/model-constraints.md)
- [Assertion aggregation contract](../contracts/assertion-aggregation.md)
