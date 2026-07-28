# Assumptions and verification-condition composition

> **Status:** Implemented in IR2
>
> **Scope:** typed assumptions and the executable verification condition

Older design material called this concern “assertion aggregation”. The current
implementation does not create an `AggregatedAssertionSet` object. Composition
is owned by `IR2Builder`, and its result is stored directly in
`VerificationTaskIR2`.

## Inputs

| Input | Producer | IR2 source tag |
|---|---|---|
| normalized public property | NNF-normalized IR1 | `spec_formula` |
| typed domain restrictions | `DomainAssumptionEncoder` | `DOMAIN` |
| resolved inline/reference anchors | `AnchorAssumptionEncoder` | anchor/provenance metadata |
| fitted model equations | selected model encoder | `MODEL` |
| explicitly supplied global assumptions | internal caller | declared source |

Every assumption is an `AssumptionIR2` containing a backend-neutral NNF formula,
source, optional description, and metadata.

## Composition

`AssumptionCollector` validates and freezes the supplied assumptions.
`VerificationConditionBuilder` then combines them with the property according to
`VerificationSemantics`.

```text
Γ = domain assumptions ∧ anchor assumptions ∧ model assumptions
```

| Semantics | Condition |
|---|---|
| `UNIVERSAL_REFUTATION` | `Γ ∧ ¬P` |
| `EXISTENTIAL_WITNESS` | `Γ ∧ P` |

The result is retained in `VerificationTaskIR2.verification_condition`; the
original normalized property remains separately available as `spec_formula`.

## Why assumptions remain explicit

Keeping `task.assumptions` separate from the executable condition supports:

- assumption-consistency diagnostics;
- source and model provenance;
- backend capability analysis;
- report counts and explanations;
- replay and debugging;
- prevention of vacuous proofs caused by an empty admissible set.

The Z3 runner may translate assumptions alone to diagnose inconsistency, subject
to the remaining execution budget.

## Model equations

Model encoders receive the exact evaluation identities found in the property.
They emit one equation for each requested evaluation and none for unreferenced
points. IR2 guardrails diagnose missing, duplicate, unrequested, or disconnected
equations.

This is the implemented convergence between the compiler and ModelBridge:

```text
requested ModelEvaluationIR
+ ModelSchema
→ model AssumptionIR2
→ VerificationTaskIR2
```

## Backend relationship

Assumption composition is backend-neutral. Z3 translation happens later, after
the router confirms that the selected backend supports every requirement
introduced by the property and assumptions.

No capability constraint is inserted as a logical assumption. Unsupported
capability is a routing failure, not part of `Γ`.

## Invariants

1. The property and assumptions remain distinguishable.
2. Every assumption has a declared source.
3. Open and closed domain bounds are preserved.
4. Model assumptions use exact requested point/output identities.
5. Universal and existential semantics select different conditions.
6. No backend object enters `VerificationTaskIR2`.
7. Assumption inconsistency cannot be reported as an ordinary property proof
   without diagnostic evidence.

## Related contracts

- [Assertion aggregation contract](../contracts/assertion-aggregation.md)
- [Typed domains as assumptions](../contracts/quantified-domain-scalar-expressions.md)
- [Model constraints](../contracts/model-constraints.md)
- [IR1 to IR2](../contracts/ir1-to-ir2.md)
