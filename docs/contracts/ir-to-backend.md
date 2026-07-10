# IR to Backend Contract

> Status: P0 / Accepted target backend boundary  
> Scope: Capability-checked IR2/LoweredQuery to BackendQuery  
> Audience: backend authors, router authors and solver integration authors

## Purpose

This is the first boundary allowed to create backend-native artifacts.

It answers:

```text
Can this backend represent every requirement of this verification task exactly?
```

---

## Inputs

```text
VerificationTaskIR2 or LoweredQuery
+ BackendSelection
+ BackendCapabilities
+ model encoding context
```

The input already contains:

- resolved scalar expressions;
- normalized logical formula;
- domain/model assumptions;
- verification semantics;
- explicit requirements;
- provenance.

---

## Compatibility Gate

Backend compilation starts only after:

```text
task.requirements ⊆ backend.capabilities
```

The gate must distinguish at least:

- boolean logic;
- equality and ordered comparisons;
- affine arithmetic;
- nonlinear multiplication;
- symbolic division;
- required scalar sorts;
- finite-set membership/equality expansion;
- symbolic categorical literals;
- domain assumptions;
- model assumptions;
- normal forms;
- universal-refutation or existential-witness execution semantics.

A single `supports_numeric_comparisons` flag is insufficient for the target language.

---

## Backend Output

A successful compiler produces:

```text
BackendQuery
```

containing backend-native:

- variable declarations with sorts;
- scalar expressions;
- boolean assertions;
- model constraints;
- execution semantics metadata;
- source-to-backend trace mapping.

---

## Exactness Rule

The backend compiler must encode the accepted IR exactly under the declared semantics.

It must not:

- coerce categorical symbols to arbitrary reals without a declared sound encoding;
- replace open bounds with closed bounds;
- ignore unsupported finite-set members;
- drop arithmetic terms;
- linearize symbolic products silently;
- replace symbolic division with a constant;
- treat `exists` SAT as a counterexample;
- invent missing bindings.

An unsupported requirement causes a routing or backend-compilation diagnostic.

---

## Sort Mapping

Backend sort mapping is driven by canonical FORML scalar types.

Examples:

| FORML type | Possible Z3 sort |
|---|---|
| INT | `Int` |
| REAL | `Real` |
| BOOL | `Bool` |
| STRING | `String` when supported by the profile |
| SYMBOLIC_CATEGORY | Enum/datatype/string encoding selected explicitly |

The chosen encoding must be recorded in backend metadata.

---

## Minimal Z3 Profile

The first complete Z3 profile may remain narrower than the language:

- boolean logic;
- integer/real comparisons;
- affine arithmetic;
- numeric interval assumptions;
- affine model assumptions;
- universal refutation;
- existential witness when runner/result semantics are implemented.

Categorical finite sets, strings, symbolic products or symbolic division remain incompatible until Z3 capabilities and translator support declare them explicitly.

---

## Backend-Owned Failures

This boundary owns:

- no registered compatible backend;
- requested backend lacking a required capability;
- unsupported scalar sort/encoding;
- unsupported arithmetic family;
- missing model encoder;
- invalid backend-native translation;
- inability to preserve verification semantics;
- inconsistent source-to-backend trace mapping.

It does not own syntax, binding or semantic typing errors.
