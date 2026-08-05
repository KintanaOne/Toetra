from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
import pytest
from sklearn.linear_model import LinearRegression, LogisticRegression

from toetra._cli.main import EXIT_OK, main


def test_init_generates_and_verifies_regression_smoke_specification(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    frame = pd.DataFrame(
        {
            "a": [0.0, 1.0, 2.0, 3.0],
            "score": [1.0, 3.0, 5.0, 7.0],
        }
    )
    model = LinearRegression().fit(frame[["a"]], frame["score"])
    model_path = tmp_path / "models" / "linear model.joblib"
    dataset_path = tmp_path / "models" / "reference data.csv"
    destination = tmp_path / "policies" / "generated.toetra"
    model_path.parent.mkdir()
    joblib.dump(model, model_path)
    frame.to_csv(dataset_path, index=False)

    assert (
        main(
            [
                "init",
                str(destination),
                "--model",
                str(model_path),
                "--dataset",
                str(dataset_path),
                "--target",
                "score",
            ]
        )
        == EXIT_OK
    )
    captured = capsys.readouterr()
    assert captured.out == f"{destination.resolve()}\n"
    assert captured.err == ""

    source = destination.read_text(encoding="utf-8")
    assert 'model := "../models/linear model.joblib"' in source
    assert 'dataset := "../models/reference data.csv"' in source
    assert source.count("[LOGIC]:") == 1

    assert main(["verify", str(destination)]) == 0
    verification = capsys.readouterr()
    assert "PROVED" in verification.out
    assert verification.err == ""


def test_init_generates_and_verifies_classification_smoke_specification(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    frame = pd.DataFrame(
        {
            "income": [-6.0, -5.0, -4.0, -3.0, 3.0, 4.0, 5.0, 6.0],
            "decision": ["no", "no", "no", "no", "yes", "yes", "yes", "yes"],
        }
    )
    model = LogisticRegression(random_state=0, max_iter=1000).fit(
        frame[["income"]], frame["decision"]
    )
    model_path = tmp_path / "binary.joblib"
    dataset_path = tmp_path / "binary.csv"
    destination = tmp_path / "classification.toetra"
    joblib.dump(model, model_path)
    frame.to_csv(dataset_path, index=False)

    assert (
        main(
            [
                "init",
                str(destination),
                "--model",
                str(model_path),
                "--dataset",
                str(dataset_path),
                "--target",
                "decision",
            ]
        )
        == EXIT_OK
    )
    capsys.readouterr()

    source = destination.read_text(encoding="utf-8")
    assert "where duplicate.income == sample.income" in source
    assert "target[sample].label == target[duplicate].label" in source

    assert 'dataset := "binary.csv"' in source

    assert main(["verify", str(destination)]) == 0
    verification = capsys.readouterr()
    assert "PROVED" in verification.out
    assert verification.err == ""
