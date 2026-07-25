# Quantified Domains and Scalar Expressions — Cross-Layer Contract

> Status: Accepted target contract  
> Scope: DSL, CST, AST, semantic validation, IR1, IR2, aggregation and backend boundary  
> Implementation state: Documentation-first; implementation must conform incrementally  
> Related ADRs: ADR-0013, ADR-0014, ADR-0015

## Purpose

This document is the normative cross-layer contract for the language evolution introducing:

```toetra
forall x0
exists candidate
```

structured domains:

```toetra
with domain(
    x0.a: ]0.0, 3.0],
    x0.region: {EU, US}
)
```

and scalar arithmetic comparisons:

```toetra
2 * x0.a + x0.b <= target
```

It answers:

```text
What information must each compiler artifact preserve, validate, and expose?
```

---

## Normative Example

```toetra
model := "demo.onnx"
target := MyTarget

[LOGIC]:
forall x0
    with domain(
        x0.a: [0.0, 3.0],
        x0.b: {obj1, obj2},
        x0.c: ]0.0, 3.0],
        x0.d: {0.0, 7.0},
        x0.e: ]0.0, 3.0[
    )
    => 2 * x0.a + x0.c <= target + 7
    using Z3
```

---

## Layer-by-Layer Obligations

| Layer | Must preserve or establish | Must not do |
|---|---|---|
| Source → CST | Required quantified identifier, interval delimiters, set delimiters, arithmetic precedence | Bind symbols or infer types |
| CST → AST | Typed scope, domain and scalar-expression nodes | Flatten domains or expressions into strings |
| AST contract | Structural completeness | Assume binding or backend support |
| AST → Semantic | Exact variable binding, recursive typing, domain validity, expression-family classification | Approximate unsupported expressions |
| Semantic → IR1 | Resolved symbols, typed scalar tree, typed domain, quantifier kind | Produce solver objects |
| IR1 → IR2 | Preserve comparison atoms, lower domain constraints to provenanced assumptions, compute requirements | Rewrite arithmetic algebraically without a sound rule |
| Aggregation | Compose domain/model/property formulas according to quantifier semantics | Treat `forall` and `exists` identically |
| IR → Backend | Match requirements to declared capabilities | Accept unsupported constructs silently |
| Backend | Produce exact backend expressions | Repair invalid semantics |

---

## Quantified Binding Invariant

Given:

```toetra
forall x0
```

all downstream artifacts must preserve one source-level binding identity corresponding to `x0`.

The traceability chain is:

```text
source token `x0`
→ CST identifier
→ QuantifierExprNode.variable
→ SymbolTable symbol
→ SemanticContext variable
→ ScopeIR variable
→ backend symbol metadata
```

An implementation may sanitize the concrete solver symbol, but it must retain a reversible mapping to the source identifier.

### Explicit references

Every explicitly qualified input reference must resolve to a variable declared by the enclosing scope.

```toetra
forall x0 => x0.a <= 3
```

is valid.

```toetra
forall x0 => y.a <= 3
```

is invalid.

The semantic validator must not use a single-variable alias fallback for an explicit unknown entity.

### Implicit references

In assertions, an unqualified feature may resolve through the scope's default entity:

```toetra
forall x0 => a <= 3
```

becomes semantically equivalent to:

```toetra
forall x0 => x0.a <= 3
```

The raw syntax remains available for diagnostics; semantic annotations store the resolved form.

### `target`

`target` resolves to the model output declared by the header. It is not an input variable and is not required to match the quantified identifier.

---

## Domain Invariant

A domain is a typed conjunction of restrictions over scope variables.

Each entry has:

```text
explicitly qualified subject
+
typed domain constraint
+
source provenance
```

The initial constraint families are:

```text
IntervalDomain
FiniteSetDomain
```

### Subject binding

Domain subjects are always explicit:

```toetra
x0.a: [0, 3]
```

The following are invalid:

```toetra
a: [0, 3]
y.a: [0, 3]
target: [0, 3]
```

### Interval preservation

The representation must preserve lower and upper expressions independently from boundary kinds.

```text
[a, b]  → CLOSED, CLOSED
]a, b]  → OPEN, CLOSED
[a, b[  → CLOSED, OPEN
]a, b[  → OPEN, OPEN
```

Boundary kinds are enum-like values, never positional booleans.

### Finite-set preservation

```toetra
x0.d: {0.0, 7.0}
```

is a two-member discrete set, not an interval.

Unquoted identifiers such as `EU` or `obj1` inside finite sets are symbolic categorical literals, not input references.

### Arithmetic bounds

Bounds may contain scalar arithmetic expressions that reference explicitly qualified input features from the enclosing scope.

```toetra
x0.a: [x0.b - 1, x0.b + 1]
```

`target` is prohibited in domain bounds.

Domain entries have simultaneous logical semantics and no source-order evaluation semantics.

---

## Scalar Expression Invariant

A comparison is:

```text
ScalarExpression comparison_operator ScalarExpression
```

Scalar expressions are recursively formed from:

- constants;
- input-feature references;
- `target`;
- unary `+` and `-`;
- binary `+`, `-`, `*`, `/`;
- parenthesized expressions.

The AST and IR must preserve source precedence and operand order.

### Initial executable profile

The first complete profile is affine:

- addition and subtraction;
- unary signs;
- multiplication by a numeric constant;
- division by a non-zero numeric constant.

The language model may represent broader trees, but unsupported symbolic products or denominators must be rejected by requirement/capability analysis. They must not be linearized or approximated silently.

---

## Logical Normalization Invariant

NNF, CNF and DNF treat a complete comparison as one logical atom.

For:

```toetra
x0.a + 2 * x0.b <= target
```

logical normalization may negate or relocate the comparison atom, but it does not distribute, reorder or simplify the internal arithmetic tree unless a separate proven scalar-rewrite pass is introduced.

---

## Domain Lowering Invariant

Typed domains remain structured through IR1.

Before verification-condition composition, each domain entry is lowered into one or more backend-independent assumptions carrying:

```text
AssumptionSource.DOMAIN
```

Examples:

```text
x0.a: ]0, 3]
→ x0.a > 0
  AND x0.a <= 3
```

```text
x0.region: {EU, US}
→ x0.region == EU
  OR x0.region == US
```

Multiple entries are conjoined.

Generated assumptions retain provenance to:

- the original property;
- the domain entry;
- the subject;
- the relevant bound or set member;
- source location when available.

---

## Quantifier Verification Semantics

### Universal property

For:

```toetra
forall x0 with domain(...) => P
```

universal proof by refutation uses:

```text
Γdomain(x0)
AND Γmodel(x0, target)
AND NOT P(x0, target)
```

- `UNSAT` means the universal property is proved for the admissible domain.
- `SAT` yields a counterexample.
- `UNKNOWN` yields no proof.

### Existential property

For:

```toetra
exists x0 with domain(...) => P
```

witness search uses:

```text
Γdomain(x0)
AND Γmodel(x0, target)
AND P(x0, target)
```

- `SAT` yields a witness and satisfies the existential request.
- `UNSAT` proves that no admissible witness exists.
- `UNKNOWN` yields no conclusion.

A runner must not label these outcomes using universal-only vocabulary.

---

## Capability Invariant

IR requirements must distinguish at least:

- boolean logic;
- scalar equality/order comparisons;
- affine arithmetic;
- nonlinear multiplication;
- symbolic division;
- interval-domain assumptions;
- finite-set membership;
- categorical symbolic literals;
- required scalar sorts;
- model assumptions;
- verification semantics (`universal_refutation`, `existential_witness`).

A backend is compatible only when it declares every required capability.

---

## Failure Ownership

| Failure | Boundary |
|---|---|
| Missing identifier after quantifier | Source → CST |
| Lost identifier or malformed tree | CST → AST |
| Explicit entity mismatch | AST → Semantic |
| Implicit subject in domain | AST → Semantic |
| Duplicate domain subject | AST → Semantic |
| Empty/reversed constant interval | AST → Semantic |
| Non-numeric arithmetic operand | AST → Semantic |
| Literal division by zero | AST → Semantic |
| Missing resolved symbol in IR lowering | Semantic → IR1 |
| Invalid normal form or assumption provenance | IR1 → IR2 |
| Wrong `forall`/`exists` composition | Aggregation invariant failure |
| Unsupported arithmetic/category/sort | Routing or backend boundary |

---

## Deferred Extensions

The following are outside this contract:

- multiple variables in one quantifier;
- nested quantifiers and shadowing;
- arbitrary relational domain predicates;
- sequence or collection expressions;
- exponentiation and functions;
- automatic nonlinear approximation;
- a mandatory categorical solver encoding.
