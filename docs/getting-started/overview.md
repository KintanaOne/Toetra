# Getting started

Toetra V1 verifies declared behavioral properties of a narrow numeric-affine ML
profile. Begin with a self-contained demo, then replace its temporary artifacts
with a supported fitted model, reference dataset, and `.toetra` policy.

## Requirements

- Python 3.11 or 3.12
- finite transformed numeric features
- fitted single-output scikit-learn `LinearRegression`, or direct fitted binary
  `LogisticRegression`
- one regression or binary-classification output

## Fastest path

```bash
python -m pip install .
make demo-quickstart
```

The quickstart exercises the public regression route. Its single Python file
can also be copied outside the checkout after installation:

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

## Reading order

1. [Installation](installation.md)
2. [First Toetra property](first-property.md)
3. [End-to-end preview](end-to-end-preview.md)
4. [Public V1 profile](../public-v1-profile.md)

The broader architecture documentation includes future extension points. The
public V1 profile is authoritative when a status statement differs.
