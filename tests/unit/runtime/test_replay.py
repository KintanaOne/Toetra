from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression

from toetra import ReplayUnavailableError, verify
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema

_SOURCE = """
model := "model.joblib"
target := score

[LOGIC]:
forall x0
    with domain(x0.a: [0.0, 3.0])
    => target < 7.0
    using Z3
"""


def _schema() -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features={"a": FeatureSchema(name="a", dtype=EnumDataType.FLOAT)},
        target="score",
        task="regression",
        target_dtype=EnumDataType.FLOAT,
        metadata={
            "linear": {
                "coef": [2.0],
                "intercept": 1.0,
                "feature_names": ["a"],
            }
        },
    )


def _model() -> LinearRegression:
    frame = pd.DataFrame({"a": [0.0, 1.0, 2.0, 3.0], "score": [1.0, 3.0, 5.0, 7.0]})
    return LinearRegression().fit(frame[["a"]], frame["score"])


def test_finding_replays_attached_artifact_model(tmp_path: Path) -> None:
    model = _model()
    frame = pd.DataFrame({"a": [0.0, 1.0, 2.0, 3.0], "score": [1.0, 3.0, 5.0, 7.0]})
    model_path = tmp_path / "model.joblib"
    dataset_path = tmp_path / "data.csv"
    joblib.dump(model, model_path)
    frame.to_csv(dataset_path, index=False)

    finding = verify(
        _SOURCE, model=model_path, dataset=dataset_path
    ).first_counterexample
    assert finding is not None

    replay = finding.replay()
    assert replay.inputs == {"a": 3}
    assert replay.backend_outputs == {"score": 7}
    record = replay.to_record()
    assert record["toetra_score"] == 7
    assert "forml_score" not in record
    assert replay.is_consistent is True
    assert replay.max_absolute_error is not None
    assert replay.max_absolute_error < 1e-12
    assert replay.to_dataframe().shape == (1, 5)
    assert "Counterexample Replay" in replay.to_text()
    assert "Counterexample replay" in replay._repr_html_()


def test_schema_only_session_requires_an_explicit_model_for_replay() -> None:
    finding = verify(_SOURCE, schema=_schema()).first_counterexample
    assert finding is not None

    try:
        finding.replay()
    except ReplayUnavailableError as error:
        assert "Pass model" in str(error)
    else:
        raise AssertionError("schema-only replay should require a model")

    assert finding.replay(_model()).is_consistent is True
