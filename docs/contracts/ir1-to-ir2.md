# IR1 to IR2 Contract

> Status: P0 / Accepted target normalization and assumption lowering  
> Scope: IR1 logical task to IR2 verification task  
> Audience: IR2 maintainers, normalizer authors and backend-router authors

## Purpose

This boundary normalizes boolean logic, materializes assumptions and calculates backend-facing requirements without creating backend objects.

---

## Inputs

```text
VerificationTaskIR1
+ optional ModelAssumptions
+ selected/derived normal-form policy
```

IR1 preconditions include resolved scalar expressions and typed domains.

---

## Outputs

Conceptually, IR2 contains:

- normalized property formula;
- domain assumptions;
- model assumptions;
- quantifier/verification semantics;
- final or composable verification condition;
- explicit requirements;
- provenance and diagnostics.

---

## Comparison Atom Rule

A complete scalar comparison remains one logical atom through NNF, CNF and DNF.

Logical normalization may:

- remove implications;
- push negation to atoms;
- distribute boolean conjunction/disjunction according to selected form;
- represent atom polarity explicitly.

It must not inspect arithmetic nodes as boolean operators or silently rewrite scalar algebra.

---

## Domain Assumption Lowering

Typed `DomainIR1` entries lower to backend-independent assumptions tagged:

```text
AssumptionSource.DOMAIN
```

### Interval

```text
subject: [lower, upper]
```

lowers to the conjunction of the applicable lower and upper comparisons.

Boundary mapping:

| Boundary | Lower operator | Upper operator |
|---|---|---|
| Closed | `>=` | `<=` |
| Open | `>` | `<` |

### Finite set

```text
subject: {v1, v2, ...}
```

lowers to:

```text
subject == v1 OR subject == v2 OR ...
```

All domain entries are conjoined.

Every generated comparison or group retains provenance to the source domain entry.

---

## Model Assumptions

Model assumptions remain separately tagged:

```text
AssumptionSource.MODEL
```

They connect input variables to the model output and other encoded model behavior.

Domain and model assumptions are not merged into anonymous boolean nodes before provenance has been recorded.

---

## Quantifier Semantics Preservation

IR2 records one of at least:

```text
UNIVERSAL_REFUTATION
EXISTENTIAL_WITNESS
```

This is not equivalent to a generic boolean polarity flag.

For universal refutation, the property contribution is negated.

For existential witness search, the property contribution remains positive.

The exact final composition may occur in the IR2 builder or assertion aggregator, but the semantic branch must already be explicit.

---

## Requirements Calculation

IR2 requirements are computed recursively over:

- property comparison atoms;
- domain assumptions;
- model assumptions;
- scalar expression families;
- scalar sorts/literal kinds;
- selected normal form;
- verification semantics.

Required distinctions include:

- affine arithmetic;
- nonlinear multiplication;
- symbolic division;
- finite-set equality expansion;
- categorical symbolic values;
- integer/real/bool/string/enum-like sorts;
- model assumptions;
- domain assumptions.

---

## Soundness Rules

IR1 → IR2 must not:

- drop a domain entry;
- change open to closed boundaries or vice versa;
- reinterpret a finite numeric set as an interval;
- lose quantified variable identity;
- negate an existential property as if it were universal;
- linearize nonlinear arithmetic without a documented sound transformation;
- erase assumption provenance;
- select a backend.

---

## Postconditions

A valid IR2 task is:

- backend-independent;
- explicit about normal form;
- explicit about verification semantics;
- explicit about requirements;
- complete with respect to property, domain and model assumptions supplied to the boundary;
- traceable to source-level constructs.
