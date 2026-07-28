# IR to backend contract

> **Status:** Implemented and accepted
>
> **Scope:** capability-checked `VerificationTaskIR2` to backend-private
> translation

This is the first boundary allowed to create backend-native objects.

## Inputs

```text
VerificationTaskIR2
+ BackendRegistry
+ NumericCompatibilityContext
+ BackendExecutionPolicy
```

The IR2 task already contains:

- normalized property and executable verification condition;
- typed domain, anchor, and model assumptions;
- verification semantics and actual normal form;
- explicit requirements;
- point/evaluation identities;
- diagnostics, lowering evidence, and provenance inputs.

## Qualification gate

Backend translation starts only after:

```text
task.requirements ⊆ backend.capabilities
+ numeric route is executable
+ requested execution controls are enforceable
```

The structural gate distinguishes Boolean forms, comparisons, arithmetic
families, scalar sorts, assumptions, quantifier semantics, point/evaluation
features, and model-semantic quantities.

The numeric gate distinguishes mathematical expressibility from the soundness
of the framework/encoder/backend route.

The operational gate covers timeout, cancellation, resources, deterministic
seed, and adapter-specific options.

## Route output

Successful qualification returns `BackendRoute` with:

- selected backend;
- capability profile;
- route reason;
- numeric compatibility assessment.

The route is not a native query.

## Adapter translation

The selected runner or translator consumes the routed `VerificationTaskIR2` and
creates an adapter-private artifact. The built-in Z3 adapter produces
`Z3Translation`.

There is no required shared `BackendQuery` or `LoweredQuery` class. An adapter
may choose its native representation provided that it satisfies this contract.

## Exactness rule

Translation must encode the accepted IR exactly under the declared semantics.
It must not:

- coerce an unsupported sort;
- replace open bounds with closed bounds;
- drop finite-set members, arithmetic terms, or assumptions;
- linearize nonlinear expressions silently;
- conflate point or output identities;
- treat existential SAT as a counterexample;
- invent a model equation or binding;
- bypass numeric conclusion restrictions.

An unsupported requirement is a routing or translation error.

## Result boundary

The runner normalizes native execution into `VerificationResult`, including:

- logical status;
- structured assignments;
- backend-neutral diagnostics;
- technical execution evidence.

Backend-native objects do not enter `VerificationReport`.

## Failure ownership

| Failure | Owner |
|---|---|
| unknown requested backend | registry/router |
| structural capability mismatch | router |
| non-executable numeric route | compatibility/router |
| unsupported execution control | router |
| mismatch between claimed capability and translator | adapter defect/translation error |
| timeout, resource, cancellation, native error | runner |

Syntax, binding, semantic typing, and model-family lowering failures belong to
earlier boundaries.
