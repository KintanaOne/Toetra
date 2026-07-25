from __future__ import annotations

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression

from dsl.backends.results import VerificationStatus
from dsl.runtime import verify
from dsl.semantic.types.enums import EnumDataType


def test_verify_resolves_header_model_relative_to_toetra_file(tmp_path) -> None:
    frame = pd.DataFrame(
        {
            "a": [0.0, 1.0, 2.0, 3.0],
            "score": [1.0, 3.0, 5.0, 7.0],
        }
    )
    model = LinearRegression().fit(frame[["a"]], frame["score"])

    model_path = tmp_path / "affine_score.joblib"
    dataset_path = tmp_path / "affine_score.csv"
    specification_path = tmp_path / "policy.toetra"
    joblib.dump(model, model_path)
    frame.to_csv(dataset_path, index=False)
    specification_path.write_text(
        """
model := "affine_score.joblib"
target := score

maximum_score := 7.0
witness_score := 5.0

[BOUND]:
forall x0
    with domain(x0.a: [0.0, 3.0])
    => target <= maximum_score
    using Z3

[LOGIC]:
exists x0
    with domain(x0.a: [0.0, 3.0])
    => target == witness_score
    using Z3
""".strip() + "\n",
        encoding="utf-8",
    )

    session = verify(specification_path, dataset=dataset_path)

    assert session.specification_path == specification_path.resolve()
    assert session.schema.target == "score"
    assert session.schema.target_dtype is EnumDataType.FLOAT
    assert tuple(report.status for report in session.reports) == (
        VerificationStatus.PROVED,
        VerificationStatus.WITNESS,
    )
    assert session.is_successful is True
    assert session.exit_code == 0
    assert session.reports[1].inputs[0].display_name == "x0.a"
    assert session.reports[1].outputs[0].display_name == "score"
