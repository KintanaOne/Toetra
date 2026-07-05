from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression


def create_tiny_sklearn_artifacts(tmp_path: Path) -> tuple[Path, Path]:
    dataset_path = tmp_path / "classification.csv"
    model_path = tmp_path / "model.joblib"

    data = pd.DataFrame(
        {
            "age": [18, 25, 32, 40, 58, 65],
            "income": [900.0, 1200.0, 1800.0, 2600.0, 4000.0, 5000.0],
            "is_active": [True, True, False, True, False, False],
            "MyTarget": [0, 0, 0, 1, 1, 1],
        }
    )

    data.to_csv(dataset_path, index=False)

    X = data[["age", "income", "is_active"]]
    y = data["MyTarget"]

    model = LogisticRegression(max_iter=200)
    model.fit(X, y)

    joblib.dump(model, model_path)

    return model_path, dataset_path
