# Backend translation artifact

> **Status:** Implemented per adapter
>
> **Filename note:** retained for stable links from earlier design documents

Toetra does not define one generic `BackendQuery` class. The stable internal
boundary is a validated, routed `VerificationTaskIR2`; each backend adapter
creates its own native translation after route qualification.

## Shared boundary

```text
VerificationTaskIR2
+ BackendRoute
+ BackendExecutionPolicy
→ registered BackendRunner
```

The IR2 task already contains the complete verification condition, assumptions,
requirements, normal form, semantics, and traceable identities. `BackendRoute`
proves that the selected backend declared compatible structural, numeric, and
operational capabilities.

## Z3 artifact

The built-in adapter uses:

```text
VerificationTaskIR2
→ Z3Translator.translate(...)
→ Z3Translation
→ Z3Runner
```

`Z3Translation` is private to the Z3 adapter. It stores the translated formula
and symbol information required to reconstruct assignments. Z3 expressions do
not flow back into IR2 or public reports.

## Adapter freedom

A future backend may use an object graph, serialized request, native model
network, or another representation. It must not require the compiler to add a
solver-specific shared IR.

Every adapter must still:

- reject unsupported IR2 requirements;
- preserve verification semantics and numeric sorts;
- maintain point/output identity and reverse assignment mapping;
- obey the backend execution contract;
- normalize its result into `VerificationResult`;
- expose no backend object through the public `toetra` facade.

## Error ownership

| Failure | Owner |
|---|---|
| no structurally/numerically/operationally compatible backend | router |
| unsupported node despite claimed capability | translator defect or structured translation error |
| timeout/resource/cancellation | runner execution evidence |
| native backend exception | structured backend execution error |
| public conclusion not permitted by an approximate lowering | post-execution compatibility policy |

## Contracts

- [IR to backend](../contracts/ir-to-backend.md)
- [Backend execution](../contracts/backend-execution-contract.md)
- [Verification provenance](../contracts/verification-provenance.md)
