# First FORML property

Create `policy.toetra`:

```toetra
model := "affine_score.joblib"
target := score

maximum_score := 7.0

[BOUND]:
forall x0
    with domain(x0.a: [0.0, 3.0])
    => target <= maximum_score
    using Z3
```

This property asks whether the extracted affine model output is at most `7.0` for
every value of feature `a` in the closed interval `[0.0, 3.0]`.

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

The V1 route proves properties of `forml.real_affine_extracted_model`, not a
bit-exact model of sklearn floating-point execution. The report records that
numeric scope explicitly.


## First binary-classification property

```toetra
model := "binary_decision.joblib"
target := decision

[LOGIC]:
forall applicant
with domain(applicant.income: [3.0, 6.0])
=> target[applicant].label == "yes" using Z3

[LOGIC]:
exists applicant
with domain(applicant.income: [3.0, 6.0])
=> target[applicant].probability("yes") >= 0.80 using Z3
```

The user never writes the logistic decision value. FORML records the lowering,
numeric policy, and concrete sklearn replay in the resulting evidence.
