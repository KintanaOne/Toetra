# Cleveland heart-disease training workspace

This scenario prepares a deterministic binary-classification workspace from the
Cleveland heart-disease dataset. It is intentionally kept under `demo/` because
it combines data preparation, model training, schema export, and generated
artifacts rather than serving as an installed package resource.

Run it from the repository root:

```bash
python demo/classification/cleveland/train.py
```

The script reads the immutable input dataset from:

```text
demo/classification/cleveland/data/heart-disease-cleveland.csv
```

It writes local, ignored artifacts to:

```text
demo/classification/cleveland/artifacts/
├── heart_clean.csv
├── heart_model.joblib
└── schema.json
```

The current Toetra V1 model bridge supports direct fitted binary
`LogisticRegression` estimators. This workspace intentionally trains a
scikit-learn preprocessing `Pipeline`, so it documents a realistic preparation
flow and a future framework-extension target; it is not presented as a V1
verification quickstart.
