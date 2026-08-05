from __future__ import annotations

from pathlib import Path

import pytest
import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression

from tests.support.backend_tasks import linear_schema
from toetra._runtime.api import _load_specification, _resolve_model
from toetra._runtime.errors import VerificationConfigurationError

_SOURCE = """
model := "artifacts/linear.joblib"
target := score
dataset := "data/reference.csv"

[BOUND]:
forall x0
with domain(x0.a: [0.0, 3.0])
=> target[x0] <= 7.0 using Z3
"""


def _write_artifacts(root: Path) -> tuple[Path, Path, Path]:
    frame = pd.DataFrame(
        {
            "a": [0.0, 1.0, 2.0, 3.0],
            "score": [1.0, 3.0, 5.0, 7.0],
        }
    )
    model = LinearRegression().fit(frame[["a"]], frame["score"])
    model_path = root / "artifacts" / "linear.joblib"
    dataset_path = root / "data" / "reference.csv"
    specification_path = root / "policy.toetra"
    model_path.parent.mkdir(parents=True)
    dataset_path.parent.mkdir(parents=True)
    joblib.dump(model, model_path)
    frame.to_csv(dataset_path, index=False)
    specification_path.write_text(_SOURCE, encoding="utf-8")
    return specification_path, model_path, dataset_path


def test_header_dataset_is_loaded_and_resolved_relative_to_specification(
    tmp_path: Path,
) -> None:
    specification_path, model_path, dataset_path = _write_artifacts(tmp_path)

    loaded = _load_specification(specification_path)
    resolved = _resolve_model(
        loaded,
        model=None,
        dataset=None,
        target=None,
        schema=None,
    )

    assert loaded.dataset_reference == "data/reference.csv"
    assert resolved.model_path == model_path.resolve()
    assert resolved.dataset_path == dataset_path.resolve()


def test_explicit_dataset_overrides_header_reference(
    tmp_path: Path,
    monkeypatch,
) -> None:
    specification_path, _, header_dataset = _write_artifacts(tmp_path)
    override_directory = tmp_path / "pipeline"
    override_directory.mkdir()
    override_dataset = override_directory / "candidate.csv"
    pd.read_csv(header_dataset).to_csv(override_dataset, index=False)
    monkeypatch.chdir(override_directory)

    loaded = _load_specification(specification_path)
    resolved = _resolve_model(
        loaded,
        model=None,
        dataset="candidate.csv",
        target=None,
        schema=None,
    )

    assert resolved.dataset_path == override_dataset.resolve()


def test_header_dataset_remains_available_with_explicit_schema(
    tmp_path: Path,
) -> None:
    specification_path, _, dataset_path = _write_artifacts(tmp_path)
    loaded = _load_specification(specification_path)

    resolved = _resolve_model(
        loaded,
        model=None,
        dataset=None,
        target=None,
        schema=linear_schema(),
    )

    assert resolved.model_path is None
    assert resolved.dataset_path == dataset_path.resolve()


def test_missing_header_dataset_fails_instead_of_being_ignored(
    tmp_path: Path,
) -> None:
    specification_path, _, dataset_path = _write_artifacts(tmp_path)
    dataset_path.unlink()
    loaded = _load_specification(specification_path)

    with pytest.raises(
        VerificationConfigurationError,
        match="Reference dataset not found",
    ) as captured:
        _resolve_model(
            loaded,
            model=None,
            dataset=None,
            target=None,
            schema=None,
        )

    assert captured.value.code == "MODEL_DATASET_NOT_FOUND"
    assert captured.value.path == str(dataset_path)


def test_explicit_dataset_override_can_replace_missing_header_dataset(
    tmp_path: Path,
) -> None:
    specification_path, _, header_dataset = _write_artifacts(tmp_path)
    override_dataset = tmp_path / "override.csv"
    pd.read_csv(header_dataset).to_csv(override_dataset, index=False)
    header_dataset.unlink()
    loaded = _load_specification(specification_path)

    resolved = _resolve_model(
        loaded,
        model=None,
        dataset=override_dataset,
        target=None,
        schema=None,
    )

    assert resolved.dataset_path == override_dataset.resolve()
