# Adding a backend

> **Audience:** IR2, backend, compatibility, runtime, reporting, and release maintainers
>
> **Boundary:** private built-in extension; Z3 remains the only public V1 backend

A backend adapter consumes a qualified `VerificationTaskIR2`, creates a native
query, executes it, and returns a backend-neutral `VerificationResult`.

It does not parse source, validate model framework objects, invent model
equations, or reinterpret public observables.

## Current backend boundaries

| Concern | Current source boundary | Required artifact |
|---|---|---|
| DSL identity | `src/toetra/_language/vocabulary/backends.py` | canonical `EnumBackend` value and accepted spellings |
| Semantic allowlist | `src/toetra/_compiler/semantic/rules/backend.py` | explicit property/backend policy |
| Structural qualification | `BackendCapabilities` | exact IR2 and execution capabilities |
| Capability registration | `create_default_backend_registry()` | built-in routing entry |
| Numeric semantics | `BackendProfileDescriptor` | adapter/version/profile/non-finite policy |
| Native translation | `BackendTranslator` protocol and adapter package | adapter-private translation artifact |
| Execution | `BackendRunner` protocol | normalized result plus execution evidence |
| Runner registration | `create_default_backend_runner_registry()` | routed backend-to-runner entry |
| Route soundness | numeric compatibility registry | evidence-backed complete-route rules |
| Presentation | generic report/provenance builders | no backend-native object leakage |

`BackendRegistry` stores capabilities; `BackendRunnerRegistry` stores
executors. Registering only one leaves an incomplete route.

## Implementation sequence

### 1. Define the adapter contract

Record:

- backend family and concrete engine/service version;
- supported verification semantics and normal forms;
- Boolean, comparison, arithmetic, sort, domain, quantifier, neighborhood, and
  model-quantity support;
- numeric semantics, rounding, range, and special-value policy;
- timeout, cancellation, resources, determinism, and native-option behavior;
- SAT/UNSAT/UNKNOWN interpretation for refutation and satisfaction tasks;
- assignment extraction and diagnostic limits.

Use an ADR when the adapter introduces a new semantic target, approximation, or
remote trust boundary.

### 2. Add vocabulary without claiming support

If users may request the backend in `.toetra`, update both
`official_backends` and `EnumBackend`. Regenerate
`src/toetra/_language/grammar/toetra_grammar.lark` from the EBNF:

```bash
python -m toetra._language.tools.generator
```

Never edit the generated Lark grammar directly. Parser acceptance is only
vocabulary availability; the semantic allowlist and public profile still
control executable support.

Update `V1_SUPPORTED_BACKENDS` and `PROPERTY_BACKEND_COMPATIBILITY` only after
the complete route is ready. Until then, a reserved backend must be rejected
with an explicit semantic error.

### 3. Declare honest capabilities

Create one immutable `BackendCapabilities` value. Every `True`, supported sort,
normal form, semantic mode, and execution control is a testable promise.

The router compares this declaration with `IR2Requirements` and
`BackendExecutionPolicy` before execution. It must reject:

- unsupported IR2 structure;
- excessive model-evaluation counts;
- unsupported generic execution controls;
- missing backend numeric profile;
- a structurally valid but numerically unqualified route.

Do not compensate for a translator limitation by weakening requirement
extraction.

### 4. Implement private translation

Implement `BackendTranslator.translate(task)`. The native translation class is
adapter-private; Toetra does not require a shared `BackendQuery` type.

Translation must preserve:

- verification semantics;
- all assumptions and the verification condition;
- scalar sorts, open/closed bounds, finite sets, and arithmetic operators;
- model, point, output, and internal-quantity identities;
- the distinction between source outputs and auxiliary quantities.

Reject an unsupported node explicitly. Do not coerce sorts, close open bounds,
drop assumptions, linearize silently, or inspect a framework estimator.

### 5. Implement normalized execution

Implement `BackendRunner.run(task, policy=...)`. The timeout covers translation
and execution as one total property budget.

Map native outcomes into two separate dimensions:

- `VerificationStatus` for the logical conclusion;
- `BackendExecutionStatus` in `BackendExecutionEvidence` for the technical
  termination.

Timeout, resource exhaustion, cancellation, or native unknown produce a
justified logical `UNKNOWN`. Technical adapter failures raise
`BackendExecutionError` with error evidence; they are not verification
findings.

Return assignments as backend-neutral Python values with stable identity
metadata. Native solver expressions, sessions, tensors, or service handles must
not enter `VerificationResult` or reports.

### 6. Register both halves

Register capabilities in `create_default_backend_registry()` and the runner in
`create_default_backend_runner_registry()`.

During unit tests, custom registries may be injected through private runtime
hooks. This is component validation only. A built-in route must work through
the default `verify(...)` path and from an installed wheel.

Registration order is routing policy when no backend is requested: the first
compatible registered backend wins. Any change to that order requires
deterministic routing tests and an explicit compatibility review.

### 7. Register numeric routes

Create a `BackendProfileDescriptor` that identifies backend kind, adapter,
version, concrete numeric profile, and non-finite policy. Add compatibility
rules for each supported source-model/encoder/property combination.

Structural capability is not numeric soundness. An adapter can translate real
arithmetic while still being incompatible with the concrete source execution.
Rules must state classification, conclusion scope, permitted conclusions,
evidence, preconditions, and replay requirements.

Test no-match and ambiguous-match behavior. Do not add a broad wildcard fallback
to hide missing evidence.

### 8. Preserve reporting and provenance

Generic reporting already consumes `BackendRoute` and `VerificationResult`.
Extend it only when backend-neutral evidence is genuinely missing.

Every route must preserve:

- selected backend and route reason;
- capability/numeric rule identity;
- native backend status;
- normalized logical status;
- execution policy snapshot, duration, and termination reason;
- diagnostics and assignment identities;
- adapter and engine versions in provenance.

All renderers and JSON must agree. Backend-native terminology can appear as
diagnostic detail, but it cannot redefine generic statuses.

### 9. Publish only after installed execution

Update backend overview, capability tables, public profile, generated numeric
matrices, release notes, and examples together. A vocabulary value or adapter
package alone is not public support.

The clean-wheel probe must execute a real route outside the repository. For an
optional or remote backend, also test missing dependency, unavailable service,
authentication/configuration failure, timeout, and deterministic offline
behavior as applicable.

## Test matrix

| Layer | Minimum coverage | Existing location to mirror |
|---|---|---|
| Vocabulary/semantic | canonical spellings, generated grammar, reserved rejection, property allowlist | `tests/unit/parser/`, `tests/unit/semantic/` |
| Capabilities | every supported and rejected IR2 requirement, execution controls | `tests/unit/backends/test_*capabilities.py` |
| Router | explicit selection, automatic order, no compatible backend, numeric rejection | `tests/unit/backends/test_router.py` |
| Translator | every accepted IR2 atom, sort, bound, normal form, identity, unsupported-node failure | `tests/unit/backends/<adapter>/` |
| Runner | SAT/UNSAT by semantics, unknown, timeout, resources, cancellation, deterministic seed, technical error | backend execution tests |
| Compatibility | profile match, no match, conflict, non-finite values, conclusion policy | `tests/unit/compatibility/` |
| Reporting | assignments, diagnostics, execution evidence, provenance, all renderers and JSON | `tests/unit/reporting/` |
| End to end | proved plus counterexample/witness and one inconclusive case through `verify(...)` | `tests/e2e/backends/` |
| Distribution | adapter files/dependencies included, clean installed-wheel execution | release tests and `make release-check` |

Use differential or independently checked cases where feasible. A translator
unit test that merely reproduces its own expected native syntax is not enough
evidence for semantic correctness.

## Exit checklist

- [ ] vocabulary, semantic allowlist, and public profile have distinct status;
- [ ] capabilities match translator and runner behavior exactly;
- [ ] native translation preserves every required IR2 distinction;
- [ ] logical and technical statuses remain separate;
- [ ] both capability and runner defaults are registered;
- [ ] numeric rules justify every permitted conclusion;
- [ ] reports and provenance contain no backend-native runtime objects;
- [ ] requested and automatic routing are deterministic;
- [ ] unit, contract, end-to-end, clean-install, and release gates pass.
