# Backends overview

FORML keeps backend execution behind explicit capability, numeric-compatibility,
and execution-policy contracts.

## Built-in V1 backend

Z3 is the only built-in V1 execution backend. It supports the implemented affine
numeric route, Boolean logic, numeric comparisons, domain assumptions, finite
numeric sets, and the normal forms declared by its capability profile.

The backend receives IR2 tasks and model assumptions. It does not parse `.toetra`
source or inspect framework model objects directly.

## Generic backend contract

Every backend adapter must declare:

- structural capabilities;
- supported verification semantics and normal forms;
- numeric profile and non-finite-value policy;
- timeout, resource, cancellation, and deterministic-seed capabilities;
- normalized execution evidence and diagnostics.

A backend is selected only when its capabilities and a registered numeric rule
permit the task. `TIMEOUT`, `RESOURCE_LIMIT`, and `CANCELLED` remain technical
termination states and map to an inconclusive logical result, never to a proof.

## Not built in for V1

ERAN, MILP, abstract-interpretation, runtime-monitoring, remote, and distributed
backends are extension or research targets. Their presence in vocabulary or
documentation is not an implementation claim.
