# Backend syntax

> Status: Accepted syntax; Z3-only built-in V1 execution
> Scope: Backend declarations in `.toetra` properties
> Audience: users and backend contributors

## Syntax

A backend declaration follows the assertion:

```toetra
[BOUND]:
forall applicant
=> target[applicant] <= 1 using Z3
```

Both `Z3` and `z3` normalize to the same backend identity.

The grammar also accepts optional argument syntax:

```text
using backend(name=value)
```

No DSL backend argument belongs to the public V1 profile unless the backend
contract explicitly documents its meaning. The builder preserves unique named
primitive arguments in the AST so they cannot disappear silently; semantic
validation then rejects every non-empty list in V1. Positional or duplicate
arguments fail during AST construction. Parser acceptance alone is not an
execution guarantee.

## Selection semantics

An explicit backend is a requirement:

```text
task declares backend
→ router must use that backend
→ absence or incompatibility is an error
```

Toetra does not silently fall back to another backend.

When a property omits `using ...`, the router selects the first registered
backend whose capabilities and numeric profile satisfy the IR2 task. The
built-in V1 registry contains only Z3, so omission does not currently introduce
a second built-in behavior.

## Recognized names

| Source spelling | Grammar status | V1 execution status |
|---|---|---|
| `Z3`, `z3` | accepted | public built-in backend |
| `ERAN`, `eran` | reserved | semantic rejection |
| `ZONOTOPE`, `zonotope` | reserved | semantic rejection |
| `BOX`, `box` | reserved | semantic rejection |

Reserved names exist to preserve vocabulary and produce deliberate diagnostics.
They do not announce bundled adapters, algorithms, or post-V1 delivery dates.

## Qualification boundary

Backend syntax reaches execution only after:

```text
AST backend declaration and retained arguments
→ semantic backend validation or explicit argument rejection
→ IR1 and IR2 preservation
→ model-semantic lowering
→ requirement extraction
→ capability and numeric qualification
→ backend translation and execution
```

The Z3 route can still reject a syntactically and semantically valid request
when its requirements are outside the public profile, for example:

- symbolic multiplication or division;
- categorical/string solver requirements;
- alternating quantifiers;
- unavailable model equations;
- unsupported output-observable lowering;
- incompatible numeric compatibility or conclusion policy.

Such a rejection must be explicit. The backend must never approximate an
unsupported language construct silently.

## Failure cases

### Unknown spelling

```text
using unknown_backend
```

This fails parsing because the name is not in the recognized backend
vocabulary.

### Reserved backend

```text
using ERAN
```

This parses, then fails V1 semantic backend validation.

### Registered but incompatible backend

For an injected/private registry extension, routing fails if the selected
backend does not satisfy the IR2 requirements or numeric policy. Internal
registration does not make the route public.

### Technical backend failure

Translation errors, timeout, resource exhaustion, cancellation, and native
`unknown` outcomes belong to backend execution. Reports preserve these
diagnostics separately from language compilation failures.

## Public support rule

A new backend becomes public only after its capabilities, numeric profile,
translation, execution controls, reporting, replay, tests, distribution, and
public-profile entry agree. See [Adding a backend](../development/adding-backend.md).

## Related pages

- [Language support levels](support-levels.md)
- [Public V1 profile](../public-v1-profile.md)
- [Backend overview](../backends/overview.md)
- [Backend capabilities](../backends/capabilities.md)
- [Backend orchestration](../backends/orchestration.md)
- [IR to backend contract](../contracts/ir-to-backend.md)
