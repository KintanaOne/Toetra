# Verification Task

> Status: Stabilizing with accepted quantified/domain/arithmetic target contract  
> Scope: Backend-independent unit of verification

## Purpose

A verification task is the complete backend-independent description of one property verification request.

It is more than a boolean assertion. It combines:

- property identity;
- scope and variables;
- quantifier verification semantics;
- normalized property formula;
- domain assumptions;
- model assumptions;
- backend requirements;
- provenance;
- optional backend hint.

---

## Conceptual Shape

```text
VerificationTaskIR2(
    property_type,
    scope,
    property_formula,
    assumptions,
    verification_condition,
    semantics,
    requirements,
    backend_hint,
    diagnostics,
    provenance,
)
```

Exact implementation fields may differ.

---

## Quantified Scope

For:

```forml
forall x0
```

scope metadata preserves:

```text
kind: quantified
quantifier: forall
variables: {x0: symbolic}
default_entity: x0
```

For `exists x0`, only the quantifier/verification semantics changes; the exact binding rules remain identical.

---

## Assumptions

Assumptions carry source identity.

Examples:

```text
DOMAIN → interval and finite-set restrictions
MODEL → encoded model behavior
NEIGHBORHOOD → perturbation-space restrictions
SEMANTIC → future derived semantic constraints
```

The property formula is not silently reclassified as an assumption.

---

## Verification Semantics

### Universal refutation

```text
condition = Γassumptions ∧ ¬P
```

`UNSAT` proves the property; `SAT` yields a counterexample.

### Existential witness

```text
condition = Γassumptions ∧ P
```

`SAT` yields a witness; `UNSAT` proves absence of a witness.

The task must make this distinction explicit so the runner cannot infer semantics from solver status alone.

---

## Scalar Atoms

A comparison atom may contain full scalar expression trees:

```text
2 * x0.a + x0.b <= target + 7
```

The task retains canonical scalar types and capability requirements.

Logical normal forms manipulate atom polarity/grouping without flattening arithmetic.

---

## Domain Traceability

Expanded domain assumptions retain a mapping to original entries.

For:

```forml
x0.a: ]0, 3]
```

the two generated comparison atoms share one source-domain-entry identity while identifying lower and upper components separately.

---

## Task Invariants

A backend-routable task has:

- no unresolved symbol;
- no ambiguous target reference;
- explicit quantifier verification semantics;
- explicit scalar/domain/model requirements;
- valid normal-form declaration;
- complete assumption provenance;
- no backend-native object before translation.
