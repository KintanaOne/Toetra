# Monitoring

> Status: Future direction  
> Implementation: Not implemented  
> Scope: Runtime observation and post-verification behavior tracking

## Purpose

Monitoring is a future Toetra runtime capability.

It is intended to observe verification execution, collect runtime diagnostics, and eventually support behavioral monitoring of deployed ML systems.

Monitoring is not required for the first functional V1.

## Position in the Architecture

```text
VerificationRuntime
→ VerificationResult
→ Diagnostics
→ Monitoring / Observation
```

Monitoring should be built after the core runtime is stable.

## Difference Between Verification and Monitoring

| Concept | Meaning |
|---|---|
| Verification | Checks whether a property holds under a specific backend semantics |
| Runtime diagnostics | Explains what happened during verification |
| Monitoring | Observes execution or behavior over time |
| Behavioral monitoring | Tracks model/system behavior after deployment |

Toetra V1 should focus on verification, not long-term monitoring.

## Possible Future Monitoring Targets

Future monitoring may observe:

- solver execution time,
- backend status distributions,
- repeated unknown results,
- frequent property violations,
- counterexample patterns,
- backend instability,
- model drift indicators,
- runtime verification traces.

## Runtime Observability

A future observability layer may collect:

```text
property_id
backend
query_size
assertion_count
solver_time
result_status
counterexample_size
diagnostic_level
```

This information can support:

- debugging,
- performance analysis,
- backend comparison,
- CI reporting,
- future AutoToetra decisions.

## Monitoring and AutoToetra

Monitoring may eventually feed backend selection.

For example, Toetra may learn that:

- one backend frequently times out on robustness properties,
- another backend is better for monotonicity checks,
- some query forms should be simplified before solving,
- certain model families require specialized lowering.

This belongs to the future AutoToetra direction, not the V1 scope.

## Monitoring and Miova

Miova can help test monitoring logic by generating:

- runtime boundary cases,
- expected backend failures,
- malformed result payloads,
- repeated timeout scenarios,
- diagnostic consistency checks.

However, Miova remains outside the normal runtime path.

## V1 Scope Decision

Monitoring should remain explicitly post-V1.

The V1 priority is:

```text
.toetra + model
→ semantic validation
→ IR1
→ IR2
→ route qualification
→ Z3-private translation
→ Z3 VerificationResult
```

Monitoring becomes useful after this path is stable.

## Documentation Rule

Any monitoring-related document should clearly mark the feature as:

```text
Status: Future direction
Implementation: Not implemented
```

This avoids confusing the target architecture with the current implementation.
