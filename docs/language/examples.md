
# Normative FORML Examples

> Status: Accepted language baseline  
> Scope: Explicit quantified bindings, typed domains and scalar arithmetic  
> Audience: users, compiler authors, test authors and backend authors

## Purpose

The examples in this document are normative.

Each example has a stable identifier and defines observable expectations across the compiler pipeline. Formatting may evolve, but the represented meaning must remain stable unless a later ADR supersedes it.

```text
source
→ CST
→ AST
→ SemanticValidatedAST
→ IR1
→ IR2 assumptions
→ verification condition
→ backend result
```

---

## QV-001 — Universal Target Bound

```forml
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
    => target <= 7
    using Z3
```

### Meaning

For every admissible valuation of `x0`, the model output declared by `target := MyTarget` is at most `7`.

### Binding

```text
quantifier: forall
variable: x0
role: symbolic
default_entity: x0
target reference: _model.MyTarget
```

The assertion does not need to mention `x0` textually. Model assumptions connect the quantified model inputs to the output.

### Domain expansion

```text
x0.a >= 0.0
x0.a <= 3.0
x0.b == obj1 OR x0.b == obj2
x0.c > 0.0
x0.c <= 3.0
x0.d == 0.0 OR x0.d == 7.0
x0.e > 0.0
x0.e < 3.0
```

### Universal verification condition

```text
Γdomain(x0)
AND Γmodel(x0, _model.MyTarget)
AND NOT(_model.MyTarget <= 7)
```

### Backend profile

The source, AST and semantic layers accept symbolic values such as `obj1` and `obj2`.

A backend without categorical-domain capability must reject the request as unsupported. It must not reinterpret the symbols as numeric variables or strings silently.

---

## QV-002 — Explicit Quantified Feature

```forml
model := "demo.joblib"
target := score

[BOUND]: forall applicant => applicant.age >= 18
```

Expected binding:

```text
applicant.age → declared symbolic entity `applicant`, feature `age`
```

---

## QV-003 — Implicit Quantified Feature

```forml
model := "demo.joblib"
target := score

[BOUND]: forall applicant => age >= 18
```

Expected binding:

```text
age → applicant.age
```

An unqualified feature is allowed in an assertion when the scope defines one unambiguous default entity.

---

## QE-001 — Existential Witness

```forml
model := "demo.joblib"
target := score

[LOGIC]:
exists applicant
    with domain(
        applicant.age: [18, 65],
        applicant.income: ]0, 100000]
    )
    => target >= 0.8
    using Z3
```

### Meaning

Find at least one admissible `applicant` whose model output is at least `0.8`.

### Existential verification condition

```text
Γdomain(applicant)
AND Γmodel(applicant, _model.score)
AND _model.score >= 0.8
```

### Result interpretation

| Solver result | FORML result |
|---|---|
| SAT | Witness found |
| UNSAT | No admissible witness exists |
| UNKNOWN | Existence undecided |

SAT is not a counterexample under existential witness semantics.

---

## DOM-001 — Boundary Matrix

```forml
model := "demo.joblib"
target := score

[LOGIC]:
forall x0
    with domain(
        x0.closed: [0, 3],
        x0.open_left: ]0, 3],
        x0.open_right: [0, 3[,
        x0.open: ]0, 3[
    )
    => target >= 0
```

Expected operators:

| Source | Lower operator | Upper operator |
|---|---|---|
| `[0, 3]` | `>=` | `<=` |
| `]0, 3]` | `>` | `<=` |
| `[0, 3[` | `>=` | `<` |
| `]0, 3[` | `>` | `<` |

Boundary kinds remain explicit in typed domain artifacts before expansion.

---

## DOM-002 — Numeric Finite Set

```forml
model := "demo.joblib"
target := score

[LOGIC]:
forall x0
    with domain(
        x0.level: {0.0, 7.0}
    )
    => target <= 10
```

Expected domain formula:

```text
x0.level == 0.0 OR x0.level == 7.0
```

`{0.0, 7.0}` is a discrete finite set, not an interval.

---

## DOM-003 — Symbolic Finite Set

```forml
model := "demo.joblib"
target := score

[LOGIC]:
forall x0
    with domain(
        x0.region: {EU, US, APAC}
    )
    => target <= 10
```

The identifiers `EU`, `US` and `APAC` are symbolic categorical literals in domain-value position.

Expected semantic requirement:

```text
requires_categorical_values = true
requires_finite_set_membership = true
```

---

## ARI-001 — Precedence

```forml
model := "finance.joblib"
target := risk

[LOGIC]:
forall account
    => account.revenue - 2 * account.cost + account.reserve <= target + 7
    using Z3
```

Expected scalar tree:

```text
ADD(
  SUB(
    FeatureRef(account.revenue),
    MUL(Constant(2), FeatureRef(account.cost))
  ),
  FeatureRef(account.reserve)
)
<=
ADD(TargetRef(_model.risk), Constant(7))
```

Multiplication binds more tightly than addition and subtraction. Additive operators are left-associative.

---

## ARI-002 — Unary Arithmetic

```forml
model := "demo.joblib"
target := score

[LOGIC]: forall x0 => -x0.debt + x0.assets >= 0
```

Expected scalar tree:

```text
ADD(
  NEG(FeatureRef(x0.debt)),
  FeatureRef(x0.assets)
)
>= Constant(0)
```

---

## ARI-003 — Arithmetic Domain Bounds

```forml
model := "demo.joblib"
target := score

[LOGIC]:
forall x0
    with domain(
        x0.b: [0.0, 10.0],
        x0.a: [x0.b - 1.0, x0.b + 1.0]
    )
    => x0.a + x0.b <= target
    using Z3
```

Expected domain assumptions:

```text
x0.b >= 0.0
x0.b <= 10.0
x0.a >= x0.b - 1.0
x0.a <= x0.b + 1.0
```

Domain entries are simultaneous constraints. Their textual order does not imply assignment order.

---

## ARI-004 — Initial Affine Profile

```forml
model := "demo.joblib"
target := score

[LOGIC]: forall x0 => (3 * x0.a - x0.b) / 2 <= target
```

This belongs to the initial affine profile because division is by a non-zero constant.

Equivalent internal classification:

```text
linear_or_affine = true
nonlinear = false
symbolic_division = false
```

---

## ARI-005 — Valid Language, Nonlinear Requirement

```forml
model := "demo.joblib"
target := score

[LOGIC]: forall x0 => x0.a * x0.b <= target
```

This expression is syntactically and semantically valid for numeric features.

It requires:

```text
requires_nonlinear_arithmetic = true
```

A backend supporting only affine arithmetic must reject it at capability matching, not during parsing and not by silently approximating the product.

---

## PW-001 — Pointwise Scope Remains Distinct

```forml
model := "demo.joblib"
target := score

[BOUND]: check_at x0 => target <= 7
```

`check_at x0` denotes one concrete evaluation point. It is not equivalent to `forall x0` and does not use a domain to generate symbolic valuations.

---

## Golden-Sample Rule

Each normative example should eventually provide normalized snapshots for all layers it reaches:

```text
source.forml
cst.json
ast.json
semantic.json
ir1.json
ir2.json
verification-condition.json
backend-query.json
result.json
metadata.yaml
```

Snapshots must use canonical serialization, not unstable Python `repr` output.

## Related Documents

- [Scopes](scopes.md)
- [Quantified Bindings](quantified-bindings.md)
- [Domains](domains.md)
- [Arithmetic Expressions](arithmetic-expressions.md)
- [Invalid and Unsupported Examples](invalid-examples.md)
- [Language Evolution Test Matrix](../testing/language-evolution-test-matrix.md)
