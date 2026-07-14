from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression

from forml import VerificationStatus, verify

_SOURCE = """
model := "model.joblib"
target := score

[LOGIC]:
forall x0
    with domain(x0.a: [0.0, 3.0])
    => target < 7.0
    using Z3

[LOGIC]:
exists x0
    with domain(x0.a: [0.0, 3.0])
    => target == 5.0
    using Z3
"""


def _artifacts(tmp_path: Path) -> tuple[Path, Path]:
    frame = pd.DataFrame({"a": [0.0, 1.0, 2.0, 3.0], "score": [1.0, 3.0, 5.0, 7.0]})
    model = LinearRegression().fit(frame[["a"]], frame["score"])
    model_path = tmp_path / "model.joblib"
    dataset_path = tmp_path / "data.csv"
    joblib.dump(model, model_path)
    frame.to_csv(dataset_path, index=False)
    return model_path, dataset_path


def test_session_exposes_findings_records_dataframe_and_artifacts(
    tmp_path: Path,
) -> None:
    model_path, dataset_path = _artifacts(tmp_path)
    session = verify(_SOURCE, model=model_path, dataset=dataset_path)

    assert len(session.counterexamples) == 1
    assert len(session.witnesses) == 1
    counterexample = session.first_counterexample
    witness = session.first_witness
    assert counterexample is not None
    assert witness is not None
    assert counterexample == session.counterexamples[0]
    assert witness == session.witnesses[0]
    assert counterexample.status is VerificationStatus.COUNTEREXAMPLE
    assert counterexample.input_values == {"a": 3}
    assert counterexample.output_values == {"score": 7}

    records = session.to_records()
    assert records[0]["property"] == 1
    assert records[0]["status"] == "counterexample"
    assert session.to_dataframe().shape == (2, 9)

    written = session.write_artifacts(tmp_path / "reports", formats={"html", "json"})
    assert set(written) == {"html", "json"}
    assert all(path.is_file() for path in written.values())


def test_session_rejects_unknown_artifact_format(tmp_path: Path) -> None:
    model_path, dataset_path = _artifacts(tmp_path)
    session = verify(_SOURCE, model=model_path, dataset=dataset_path)

    try:
        session.write_artifacts(tmp_path / "reports", formats={"pdf"})
    except ValueError as error:
        assert "pdf" in str(error)
    else:
        raise AssertionError("unsupported report format was not rejected")
