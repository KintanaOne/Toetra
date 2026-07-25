from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression

from toetra import VerificationSession, VerificationStatus, verify
from model.runtime.manager import ModelManager
from model.schema.model_schema import ModelSchema

SPEC_PATH = Path(__file__).with_name("affine_regression_policy.forml")
EXPECTED_STATUSES = (
    VerificationStatus.PROVED,
    VerificationStatus.COUNTEREXAMPLE,
    VerificationStatus.WITNESS,
)


def build_demo_artifacts(directory: Path) -> tuple[Path, Path]:
    """Train and serialize the tiny affine model used by the demo."""

    frame = pd.DataFrame(
        {
            "a": [0.0, 1.0, 2.0, 3.0],
            "score": [1.0, 3.0, 5.0, 7.0],
        }
    )
    model = LinearRegression().fit(frame[["a"]], frame["score"])

    model_path = directory / "affine_score.joblib"
    dataset_path = directory / "affine_score.csv"
    joblib.dump(model, model_path)
    frame.to_csv(dataset_path, index=False)
    return model_path, dataset_path


def build_demo_schema(model_path: Path, dataset_path: Path) -> ModelSchema:
    """Load the serialized model and expose its normalized FORML schema."""

    return ModelManager(
        model_path=model_path,
        dataset_path=dataset_path,
        target_name="score",
    ).build_schema()


def execute_demo(source: str, schema: ModelSchema) -> VerificationSession:
    """Compile, route and execute all properties through the public API."""

    return verify(
        source,
        schema=schema,
    )


def run_demo() -> tuple[ModelSchema, VerificationSession]:
    """Run the self-contained demo without leaving generated artifacts behind."""

    source = SPEC_PATH.read_text(encoding="utf-8")
    with TemporaryDirectory(prefix="forml-affine-demo-") as raw_directory:
        directory = Path(raw_directory)
        model_path, dataset_path = build_demo_artifacts(directory)
        schema = build_demo_schema(model_path, dataset_path)
        executions = execute_demo(source, schema)
    return schema, executions


def _model_equation(schema: ModelSchema) -> str:
    linear = schema.metadata.get("linear", {})
    coefficients = linear.get("coef", [])
    intercept = linear.get("intercept")
    feature_names = linear.get("feature_names", tuple(schema.features))
    terms = " + ".join(
        f"{coefficient}*x0.{feature}"
        for feature, coefficient in zip(feature_names, coefficients)
    )
    return f"_model.{schema.target} = {terms} + {intercept}"


def print_demo(schema: ModelSchema, session: VerificationSession) -> None:
    """Print the demo through the shared user-facing report renderer."""

    print("=" * 80)
    print("FORML — affine model, specification constants and typed domains")
    print("=" * 80)
    print(SPEC_PATH.read_text(encoding="utf-8"))
    print()
    print(f"Model framework : {schema.framework.value}")
    print(f"Model type      : {schema.model_type}")
    print(f"Model equation  : {_model_equation(schema)}")
    print(f"Target dtype    : {getattr(schema.target_dtype, 'value', None)}")
    print()
    print(session.to_text())


def main() -> None:
    schema, session = run_demo()
    statuses = tuple(report.status for report in session.reports)
    if statuses != EXPECTED_STATUSES:
        raise AssertionError(
            "Unexpected demo statuses: "
            f"expected {[status.value for status in EXPECTED_STATUSES]}, "
            f"got {[status.value for status in statuses]}"
        )

    print_demo(schema, session)
    print("✅ FORML affine end-to-end demo succeeded.")


if __name__ == "__main__":
    main()
