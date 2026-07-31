# First Toetra properties

## First regression property

This example uses the public regression route: a fitted single-output
scikit-learn `LinearRegression`. Toetra exposes its numeric prediction as
`target[point]` and encodes the extracted model as an exact-real affine
abstraction for Z3.

Create `policy.toetra`:

<!-- toetra-doc-snippet: regression-bound -->
```toetra
model := "affine_score.joblib"
target := score

maximum_score := 7.0

[BOUND]:
forall x0
with domain(x0.a: [0.0, 3.0])
=> target[x0] <= maximum_score using Z3
```

This regression property asks whether the model prediction `target[x0]` is at
most `7.0` for every value of feature `a` in the closed interval
`[0.0, 3.0]`.

Run it from Python:

```python
from toetra import verify

session = verify(
    "policy.toetra",
    model="affine_score.joblib",
    dataset="reference.csv",
)
session.print()
```

Possible universal outcomes are `PROVED`, `COUNTEREXAMPLE`, or `UNKNOWN`.
Existential properties use `WITNESS`, `NO_WITNESS`, or `UNKNOWN`.

For this `LinearRegression` route, V1 proves properties of
`toetra.real_affine_extracted_model`, not a bit-exact model of sklearn
floating-point execution. The report records that numeric scope explicitly.


## First binary-classification property

<!-- toetra-doc-snippet: binary-probability -->
```toetra
model := "binary_decision.joblib"
target := decision

[LOGIC]:
forall applicant
with domain(applicant.income: [3.0, 6.0])
=> target[applicant].probability("yes") >= 0.80 using Z3
```

The user never writes the logistic decision value. Toetra records the lowering,
numeric policy, and concrete sklearn replay in the resulting evidence. The
language reference contains additional label and existential-probability
examples.
