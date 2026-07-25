# End-to-End Preview

FORML V1 verifies numeric affine model behavior over concrete and symbolic points.

## Global bound

```toetra
model := "credit_risk.joblib"
target := RiskScore

[BOUND]:
forall applicant
with domain(
    applicant.age: [18, 90],
    applicant.income: [0, 200000],
    applicant.debt_ratio: [0.0, 1.0]
)
=> target <= 0.85 using Z3
```

With one visible point, `target` means `target[applicant]`.

## Real observation

```toetra
anchor customer := ref(
    key = "application_id",
    value = "APP-1842"
)

[BOUND]:
check_at customer
=> target <= 0.6 using Z3
```

```python
session = verify(
    specification,
    model="credit_risk.joblib",
    dataset="applications.csv",
)
```

The dataset may supply both schema/introspection evidence and the default anchor lookup source. Extra lookup columns are excluded from model features.

## Two-point monotonicity

```toetra
[MONOTONICITY]:
forall lower, higher
with domain(
    lower.income: [0, 200000],
    higher.income: [0, 200000]
)
where higher.income >= lower.income
=> target[higher] <= target[lower] using Z3
```

FORML creates two model equations, distinct Z3 outputs, grouped evidence, and a two-point replay.

## Local robustness sugar

```toetra
anchor customer := { a: 1.0 }

[ROBUSTNESS]:
at customer with perturbed in neighborhood(
    metric = Linf,
    eps = 0.1
)
=> (target[perturbed] - target[customer] <= 0.2)
   and (target[customer] - target[perturbed] <= 0.2) using Z3
```

This uses the same pipeline as the explicit `forall perturbed where perturbed in neighborhood(of = customer, ...)` form.

## Inspecting evidence

```python
for finding in session.findings:
    print(finding.status)
    print(finding.point_values)
    print(finding.output_values_by_point)

replay = session.first_counterexample.replay()
print(replay.to_dataframe())
```

The initial executable profile is deliberately narrow: numerical transformed features, scalar affine output, Z3, homogeneous quantifiers, and `Linf` neighborhoods.
