# Getting started

FORML V1 verifies declared behavioral properties of a narrow numeric-affine ML
profile. Begin with the self-contained demo, then replace its temporary artifacts
with your own fitted `LinearRegression`, reference dataset, and `.forml` policy.

## Requirements

- Python 3.11 or 3.12
- finite transformed numeric features
- fitted single-output scikit-learn `LinearRegression`
- one numeric target

## Fastest path

```bash
python -m pip install -r requirements-dev.txt
make demo-user
```

The demo exercises the public `forml.verify` API and prints a universal result and
an existential result.

## Reading order

1. [Installation](installation.md)
2. [First FORML property](first-property.md)
3. [End-to-end preview](end-to-end-preview.md)
4. [Public V1 profile](../public-v1-profile.md)

The broader architecture documentation includes future extension points. The
public V1 profile is authoritative when a status statement differs.
