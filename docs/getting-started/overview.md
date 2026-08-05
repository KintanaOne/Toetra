# Getting started

Toetra V1 verifies declared behavioral properties through two narrow public
routes: single-output linear regression and direct binary logistic
classification. Begin with the self-contained regression demo, then replace
its temporary artifacts with a supported fitted model, reference dataset, and
`.toetra` policy.

`1.0.0rc3` is an evaluation release candidate installed from a source checkout
or source archive. It is not the stable release and is not currently published
on PyPI.

## Requirements

- Python 3.11 or 3.12
- finite transformed numeric features
- fitted single-output scikit-learn `LinearRegression`, or direct fitted binary
  `LogisticRegression`
- one regression or binary-classification output

## Fastest path

From the repository root:

```bash
python -m pip install .
python -m demo.quickstart.verify_model --demo
```

The quickstart exercises the public regression route and should finish with one
`PROVED` result and one `WITNESS`.

Its single Python file can also be copied outside the checkout after
installation:

```bash
cp demo/quickstart/verify_model.py /tmp/toetra-quickstart.py
cd /tmp
python toetra-quickstart.py --demo
```

The classification demo covers label proof, counterexample replay, probability
witnessing, and pairwise label equality:

```bash
make demo-classification
```

## Create a starter policy

For an existing supported model, `toetra init` creates a `.toetra` file whose
model, target, and optional dataset declarations are immediately executable:

```bash
toetra init policy.toetra \
  --model model.joblib \
  --target score \
  --dataset reference.csv
```

The generated property is a wiring smoke test only. Replace it with a meaningful
requirement before interpreting the policy as verification evidence.

## Reading order

1. [Installation and availability](installation.md)
2. [First Toetra properties](first-property.md)
3. [End-to-end preview](end-to-end-preview.md)
4. [Public V1 profile and limitations](../public-v1-profile.md)
5. [Public Python API](../api-reference/index.md)

The broader architecture documentation includes future extension points. The
public V1 profile is authoritative when a status statement differs.
