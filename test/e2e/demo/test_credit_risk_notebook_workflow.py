from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression

from forml import VerificationStatus, verify
from forml.examples import credit_risk_policy


def test_credit_risk_notebook_workflow_runs_and_replays_counterexample(
    tmp_path: Path,
) -> None:
    rows = []
    for debt_ratio in (0.0, 0.25, 0.5, 0.75, 1.0):
        for late_payments in (0.0, 1.0, 2.0, 3.0, 4.0, 5.0):
            rows.append(
                {
                    "debt_ratio": debt_ratio,
                    "late_payments": late_payments,
                    "risk_score": 0.6 * debt_ratio + 0.08 * late_payments + 0.1,
                }
            )

    frame = pd.DataFrame(rows)
    features = ["debt_ratio", "late_payments"]
    model = LinearRegression().fit(frame[features], frame["risk_score"])

    model_path = tmp_path / "credit_risk.joblib"
    dataset_path = tmp_path / "credit_risk_reference.csv"
    joblib.dump(model, model_path)
    frame.to_csv(dataset_path, index=False)

    session = verify(
        credit_risk_policy(),
        model=model_path,
        dataset=dataset_path,
    )

    assert tuple(report.status for report in session.reports) == (
        VerificationStatus.PROVED,
        VerificationStatus.COUNTEREXAMPLE,
        VerificationStatus.WITNESS,
    )

    counterexample = session.first_counterexample
    assert counterexample is not None
    assert set(counterexample.input_values) == {"debt_ratio", "late_payments"}

    replay = counterexample.replay()
    assert replay.is_consistent is True
    assert replay.max_absolute_error is not None
    assert replay.max_absolute_error < 1e-12
    assert replay.to_dataframe().shape == (1, 6)

    artifacts = session.write_artifacts(tmp_path / "reports")
    assert artifacts["html"].is_file()
    assert artifacts["json"].is_file()
    assert "Counterexample" in artifacts["html"].read_text(encoding="utf-8")


NOTEBOOK_PATH = (
    Path(__file__).parents[3] / "demo" / "regression" / "credit_risk_validation.ipynb"
)


def test_credit_risk_notebook_executes_from_notebook_directory() -> None:
    script = f"""
import json
from pathlib import Path

notebook_path = Path({str(NOTEBOOK_PATH)!r})
notebook = json.loads(notebook_path.read_text(encoding=\"utf-8\"))
namespace = {{\"__name__\": \"__main__\"}}

for index, cell in enumerate(notebook[\"cells\"]):
    if cell.get(\"cell_type\") != \"code\":
        continue
    source = \"\".join(cell.get(\"source\", []))
    exec(compile(source, f\"{{notebook_path}}:cell-{{index}}\", \"exec\"), namespace)

session = namespace[\"session\"]
assert [report.status.value for report in session.reports] == [
    \"proved\",
    \"counterexample\",
    \"witness\",
]
assert namespace[\"replay\"].is_consistent is True
print(\"NOTEBOOK_EXECUTION_OK\")
"""

    completed = subprocess.run(
        [sys.executable, "-I", "-c", script],
        cwd=NOTEBOOK_PATH.parent,
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert completed.returncode == 0, completed.stderr
    assert "NOTEBOOK_EXECUTION_OK" in completed.stdout
