from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression

from dsl.backends.results import VerificationStatus
from dsl.runtime import verify

POLICY_PATH = (
    Path(__file__).parents[3] / "demo" / "notebooks" / "credit_risk_policy.forml"
)


def _number(value: object) -> float:
    text = str(value)
    return float(Fraction(text)) if "/" in text else float(text)


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
        POLICY_PATH,
        model=model_path,
        dataset=dataset_path,
    )

    assert tuple(report.status for report in session.reports) == (
        VerificationStatus.PROVED,
        VerificationStatus.COUNTEREXAMPLE,
        VerificationStatus.WITNESS,
    )

    counterexample = session.reports[1]
    values = {
        assignment.display_name.split(".", 1)[1]: _number(assignment.value)
        for assignment in counterexample.inputs
    }
    row = pd.DataFrame([values], columns=features)
    actual_prediction = float(model.predict(row)[0])
    encoded_prediction = _number(counterexample.outputs[0].value)

    assert abs(actual_prediction - encoded_prediction) < 1e-12
    assert "FORML Verification Session" in session._repr_html_()

    html_path = session.write_html(tmp_path / "reports" / "credit-risk.html")
    assert html_path.is_file()
    assert "Counterexample" in html_path.read_text(encoding="utf-8")
