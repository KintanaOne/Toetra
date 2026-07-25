from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression

FIXTURE_DIR = Path("test/fixtures/point_binding_evaluation")


@dataclass(frozen=True)
class LinearArtifacts:
    model_path: Path
    dataset_path: Path
    model: LinearRegression


def source(name: str) -> str:
    return (FIXTURE_DIR / f"{name}.toetra").read_text(encoding="utf-8")


def build_linear_artifacts(
    tmp_path: Path,
    *,
    feature_names: Sequence[str],
    coefficients: Sequence[float],
    intercept: float,
    metadata: pd.DataFrame | None = None,
) -> LinearArtifacts:
    if len(feature_names) != len(coefficients):
        raise ValueError("feature_names and coefficients must have the same length")

    rows = max(5, len(feature_names) + 2)
    feature_values = {
        name: [float((row + 1) ** (index + 1)) for row in range(rows)]
        for index, name in enumerate(feature_names)
    }
    features = pd.DataFrame(feature_values)
    target = (
        sum(
            coefficient * features[name]
            for name, coefficient in zip(feature_names, coefficients, strict=True)
        )
        + intercept
    )

    model = LinearRegression().fit(features, target)
    model_path = tmp_path / "linear.joblib"
    dataset_path = tmp_path / "reference.csv"
    joblib.dump(model, model_path)

    dataset = features.copy()
    if metadata is not None:
        if len(metadata) != len(dataset):
            raise ValueError("metadata must contain one row per model sample")
        for name in reversed(tuple(metadata.columns)):
            dataset.insert(0, name, metadata[name].to_numpy())
    dataset["score"] = target
    dataset.to_csv(dataset_path, index=False)
    return LinearArtifacts(
        model_path=model_path, dataset_path=dataset_path, model=model
    )
