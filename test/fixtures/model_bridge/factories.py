from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression, LogisticRegression

DATA_DIR = Path(__file__).resolve().parent / "datasets"
GOLDEN_DIR = Path(__file__).resolve().parent / "golden"


def dataset_path(name: str) -> Path:
    return DATA_DIR / name


def golden_path(name: str) -> Path:
    return GOLDEN_DIR / name


def train_classification_model() -> LogisticRegression:
    data = pd.read_csv(dataset_path("classification.csv"))
    x = data.drop(columns=["MyTarget"])
    y = data["MyTarget"]

    model = LogisticRegression(max_iter=1000, random_state=0)
    model.fit(x, y)
    return model


def train_regression_model() -> LinearRegression:
    data = pd.read_csv(dataset_path("regression.csv"))
    x = data.drop(columns=["SalePrice"])
    y = data["SalePrice"]

    model = LinearRegression()
    model.fit(x, y)
    return model


def save_joblib_model(
    model: Any, tmp_path: Path, filename: str = "model.joblib"
) -> Path:
    path = tmp_path / filename
    joblib.dump(model, path)
    return path


def save_pickle_model(model: Any, tmp_path: Path, filename: str = "model.pkl") -> Path:
    path = tmp_path / filename
    with path.open("wb") as f:
        pickle.dump(model, f)
    return path


def make_classification_joblib(tmp_path: Path) -> Path:
    return save_joblib_model(
        train_classification_model(), tmp_path, "classification.joblib"
    )


def make_classification_pkl(tmp_path: Path) -> Path:
    return save_pickle_model(
        train_classification_model(), tmp_path, "classification.pkl"
    )


def make_regression_joblib(tmp_path: Path) -> Path:
    return save_joblib_model(train_regression_model(), tmp_path, "regression.joblib")


def make_regression_pkl(tmp_path: Path) -> Path:
    return save_pickle_model(train_regression_model(), tmp_path, "regression.pkl")


def schema_to_contract(schema) -> dict[str, Any]:
    """
    Convert ModelSchema to a stable golden-test contract.

    We intentionally compare only stable public contract fields and avoid
    full sklearn metadata such as learned coefficients or numpy arrays.
    """

    metadata = dict(schema.metadata or {})

    return {
        "framework": getattr(schema.framework, "value", str(schema.framework)),
        "model_type": schema.model_type,
        "task": schema.task,
        "target": schema.target,
        "features": {
            name: {
                "dtype": getattr(feature.dtype, "value", str(feature.dtype)),
                "nullable": bool(feature.nullable),
            }
            for name, feature in sorted(schema.features.items())
        },
        "metadata": {
            "serialization_format": metadata.get("serialization_format"),
            "model_class": metadata.get("model_class"),
            "module": metadata.get("module"),
            "n_features_in": _to_builtin(metadata.get("n_features_in")),
        },
    }


def load_golden(name: str) -> dict[str, Any]:
    with golden_path(name).open("r", encoding="utf-8") as f:
        return json.load(f)


def _to_builtin(value: Any) -> Any:
    if hasattr(value, "item"):
        return value.item()
    return value
