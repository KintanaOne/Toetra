from __future__ import annotations

import json
import pickle
from pathlib import Path

from tests.support.paths import FIXTURES_ROOT, GOLDEN_ROOT
from typing import Any

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression, LogisticRegression

DATA_DIR = FIXTURES_ROOT / "model_bridge"
GOLDEN_DIR = GOLDEN_ROOT / "model_bridge"


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
        "output_name": schema.output_name,
        "output_schema": output_schema_to_contract(schema.output_schema),
        "target": schema.target,
        "target_dtype": (
            schema.target_dtype.value if schema.target_dtype is not None else None
        ),
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


def output_schema_to_contract(output_schema) -> dict[str, Any]:
    contract = {
        "kind": output_schema.kind.value,
        "available_observables": [
            observable.value for observable in output_schema.available_observables
        ],
        "primary_dtype": (
            output_schema.primary_dtype.value
            if output_schema.primary_dtype is not None
            else None
        ),
        "source_dtype": output_schema.source_dtype,
    }
    if hasattr(output_schema, "labels"):
        contract["labels"] = list(output_schema.labels)
    if hasattr(output_schema, "probability_available"):
        contract["probability_available"] = bool(output_schema.probability_available)
    policy = getattr(output_schema, "decision_policy", None)
    if policy is not None:
        contract["decision_policy"] = {
            "negative_label": policy.negative_label,
            "positive_label": policy.positive_label,
            "probability_threshold": policy.probability_threshold,
            "oriented_decision_threshold": policy.oriented_decision_threshold,
            "positive_when_strictly_greater": (policy.positive_when_strictly_greater),
            "equality_label": policy.equality_label,
            "policy_source": policy.policy_source,
            "semantic_profile_id": policy.semantic_profile_id,
        }
    return contract


def load_golden(name: str) -> dict[str, Any]:
    with golden_path(name).open("r", encoding="utf-8") as f:
        return json.load(f)


def _to_builtin(value: Any) -> Any:
    if hasattr(value, "item"):
        return value.item()
    return value
