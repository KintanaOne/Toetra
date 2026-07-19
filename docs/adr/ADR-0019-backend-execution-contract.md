# ADR-0019 — Define a Backend-Neutral Execution Contract

- **Status:** Accepted
- **Date:** 2026-07-18
- **Scope:** backend routing, execution, runtime and reporting

## Context

A verification backend can be logically capable of processing a task while
still being operationally unsuitable for a requested execution policy. A
backend may not support a timeout, cooperative cancellation, a deterministic
seed, a memory ceiling or a bounded work budget.

Those controls are not Z3 concepts. They are requirements of a verification
platform and must remain valid for SMT, MILP, abstract interpretation, concrete
search, remote services and future backend families.

FORML also needs to distinguish two different outcomes:

1. the logical interpretation of a verification task (`PROVED`,
   `COUNTEREXAMPLE`, `WITNESS`, `NO_WITNESS`, `UNKNOWN`);
2. the technical termination of a backend attempt (`SAT`, `UNSAT`, `TIMEOUT`,
   `RESOURCE_LIMIT`, `CANCELLED`, `UNKNOWN`, `ERROR`).

Treating timeout or cancellation as an undifferentiated backend `unknown` loses
important audit information. Treating a technical exception as a logical
`UNKNOWN` is worse: it hides a failed execution as a legitimate inconclusive
result.

## Decision

FORML defines a backend-neutral execution contract composed of:

- `BackendExecutionPolicy`;
- `BackendResourceLimits`;
- `BackendExecutionCapabilities`;
- `BackendExecutionEvidence`;
- `BackendExecutionStatus`;
- `BackendExecutionError` for technical failures.

The default policy applies a finite 30-second timeout to every property. A
caller may explicitly disable it with `timeout_ms=None`, but a backend is never
allowed to silently ignore a requested control.

The policy may contain:

```text
timeout
abstract backend work units
memory ceiling
cooperative cancellation token
deterministic seed
adapter-specific options
```

Backend capabilities declare which controls the adapter can enforce. Routing
must reject a route before execution when the selected backend cannot honor the
requested policy.

One policy is resolved once per `verify(...)` call and passed unchanged to both
routing and execution. Each property receives its own total execution budget.
Translation, primary solving and optional backend diagnostics consume the same
budget; internal steps do not restart the timeout.

## Generic termination statuses

| Status | Meaning |
|---|---|
| `SAT` | The backend found a satisfying assignment |
| `UNSAT` | The backend proved the encoded condition unsatisfiable |
| `UNKNOWN` | The backend terminated without a more precise generic reason |
| `TIMEOUT` | The total execution deadline expired |
| `RESOURCE_LIMIT` | A declared work or memory limit was reached |
| `CANCELLED` | Cooperative cancellation interrupted or prevented execution |
| `ERROR` | A technical backend failure occurred |

`TIMEOUT`, `RESOURCE_LIMIT`, `CANCELLED` and generic `UNKNOWN` produce the FORML
logical status `UNKNOWN`, with structured diagnostics. `ERROR` raises
`BackendExecutionError` and is not reported as a logical verification result.

## Adapter responsibilities

Each backend adapter must:

1. map supported generic controls to native backend controls;
2. reject unsupported or conflicting options;
3. preserve the total policy budget across internal execution phases;
4. normalize native unknown reasons into generic execution statuses;
5. expose native details only as backend-specific evidence;
6. raise a structured execution error for technical failures.

Z3 is the first implementation. It maps:

```text
timeout_ms          → timeout
max_backend_units   → rlimit
max_memory_mb       → max_memory
deterministic_seed  → random_seed
cancellation token  → solver interrupt
```

This mapping is an adapter implementation, not the architectural contract.

## Reporting

Every completed backend attempt records:

- generic execution status;
- duration;
- generic reason;
- native backend reason, when available;
- the token-free policy snapshot actually used.

The report JSON schema is incremented to version 4. Cancellation tokens are
never serialized.

## Consequences

### Positive

- Every backend is subject to an explicit operational contract.
- Timeout and resource exhaustion are auditable rather than collapsed into a
  backend-specific string.
- Future local and remote backends can use the same runtime API.
- Technical failures remain distinguishable from legitimate inconclusive
  verification.
- Reports can support later orchestration, quotas and governance without
  changing the core result model.

### Costs

- Backend adapters must declare and test their execution capabilities.
- Adapter-specific options require validation and must not override generic
  controls.
- Cancellation is cooperative and depends on a backend exposing an interrupt
  mechanism.
- A finite default timeout can turn previously unbounded calls into explicit
  `UNKNOWN/TIMEOUT`, which is the intended fail-safe behavior.

## Alternatives considered

### Configure timeout directly in the Z3 runner

Rejected because it makes a platform requirement backend-specific and cannot be
reused by future backends.

### Treat every interruption as backend `unknown`

Rejected because timeout, cancellation and resource exhaustion have different
operational and audit meanings.

### Convert technical exceptions to logical `UNKNOWN`

Rejected because an execution failure is not a valid logical conclusion.

### Restart the timeout for every internal solver call

Rejected because a property could exceed the user-declared budget through
secondary diagnostics or retries.
