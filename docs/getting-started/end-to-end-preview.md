# End-to-End Numeric-Affine Preview

> Status: Implemented initial profile  
> Scope: FORML source + optional `ModelSchema` → Z3 result

## What works today

The current executable profile is:

```text
.forml specification
+ optional ModelSchema and supported model encoder
→ CST and AST
→ semantic binding and schema-aware scalar typing
→ IR1 recursive scalar expressions
→ NNF
→ IR2 domain/model assumption aggregation
→ backend capability routing
→ Z3 numeric-affine translation
→ structured verification result
```

## Complete example

```forml
model := "linear.joblib"
target := score

max_score := 7.0
minimum_a := 0.0
maximum_a := 3.0

[BOUND]:
forall x0
    with domain(
        x0.a: [minimum_a, maximum_a]
    )
    => target <= max_score
    using Z3
```

With the encoded model equation:

```text
score = 2 * x0.a + 1
```

FORML builds:

```text
Γdomain:
    x0.a >= 0
    x0.a <= 3

Γmodel:
    _model.score = 2 * x0.a + 1

P:
    _model.score <= 7

Universal verification condition:
    Γdomain ∧ Γmodel ∧ ¬P
```

Z3 returns `UNSAT`, which FORML interprets as:

```text
PROVED
Property proved: no counterexample exists under the encoded assumptions.
```

## Existential semantics

For:

```forml
[LOGIC]:
exists x0
    with domain(x0.a: ]0.0, 3.0])
    => x0.a > 2.0
    using Z3
```

FORML builds `Γ ∧ P`. A satisfiable query returns `WITNESS`; an unsatisfiable query returns `NO_WITNESS`.

## Capability boundary

The initial Z3 profile accepts:

- numeric `INT` and `FLOAT` scalars;
- addition, subtraction and unary signs;
- multiplication by a compile-time numeric constant;
- division by a non-zero compile-time numeric constant;
- open and closed numeric intervals;
- numeric finite sets;
- supported affine model-output equations.

It rejects before execution:

- feature × feature multiplication;
- division by a symbolic expression;
- symbolic categorical sets;
- unsupported model constraints;
- unsupported scalar sorts.

## Vacuity warning

When an UNSAT universal query is caused by inconsistent assumptions rather than the property itself, the result remains `PROVED` but includes:

```text
Z3_VACUOUS_PROOF
The property is proved only because the aggregated assumptions are inconsistent;
the admissible set is empty.
```

## Deliberate V1 limits

This profile does not yet encode:

- preprocessing pipelines;
- arbitrary sklearn models;
- trees, ensembles or neural networks;
- nonlinear arithmetic;
- symbolic categories;
- multi-variable or nested quantifier semantics;
- runtime monitoring.
