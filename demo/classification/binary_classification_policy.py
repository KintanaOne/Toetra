from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression

from forml import VerificationSession, VerificationStatus, verify

DEMO_SPEC_PATH = Path(__file__).with_name("binary_classification_policy.forml")
EXPECTED_STATUSES = (
    VerificationStatus.PROVED,
    VerificationStatus.COUNTEREXAMPLE,
    VerificationStatus.WITNESS,
    VerificationStatus.PROVED,
)


def build_demo_artifacts(directory: Path) -> tuple[Path, Path]:
    frame = pd.DataFrame(
        {
            "income": [-6.0, -5.0, -4.0, -3.0, 3.0, 4.0, 5.0, 6.0],
            "decision": ["no", "no", "no", "no", "yes", "yes", "yes", "yes"],
        }
    )
    model = LogisticRegression(random_state=0, max_iter=1000).fit(
        frame[["income"]], frame["decision"]
    )
    model_path = directory / "binary_decision.joblib"
    dataset_path = directory / "binary_decision_reference.csv"
    joblib.dump(model, model_path)
    frame.to_csv(dataset_path, index=False)
    return model_path, dataset_path


def run_demo(*, artifact_directory: Path | None = None) -> VerificationSession:
    if artifact_directory is not None:
        artifact_directory.mkdir(parents=True, exist_ok=True)
        model_path, dataset_path = build_demo_artifacts(artifact_directory)
        session = verify(DEMO_SPEC_PATH, model=model_path, dataset=dataset_path)
        session.write_artifacts(artifact_directory / "reports")
        return session

    with TemporaryDirectory(prefix="forml-binary-demo-") as raw_directory:
        root = Path(raw_directory)
        model_path, dataset_path = build_demo_artifacts(root)
        return verify(DEMO_SPEC_PATH, model=model_path, dataset=dataset_path)


def main() -> int:
    session = run_demo()
    session.print()
    actual = tuple(report.status for report in session.reports)
    if actual != EXPECTED_STATUSES:
        raise RuntimeError(f"Unexpected demo statuses: {actual!r}")
    counterexample = session.first_counterexample
    if counterexample is None:
        raise RuntimeError("The demo must expose one replayable counterexample")
    replay = counterexample.replay()
    if not replay.is_consistent or replay.assertion_satisfied is not False:
        raise RuntimeError("Classification counterexample replay is inconsistent")
    print("\nClassification counterexample replay: consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
