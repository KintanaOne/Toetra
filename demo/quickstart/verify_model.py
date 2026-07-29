from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
from tempfile import TemporaryDirectory

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression

from toetra import VerificationConfigurationError, VerificationSession, verify

DEMO_POLICY = """\
model := "affine_score.joblib"
target := score

minimum_a := 0.0
maximum_a := 3.0
maximum_score := 7.0
witness_score := 5.0

[BOUND]:
forall x0
    with domain(x0.a: [minimum_a, maximum_a])
    => target <= maximum_score
    using Z3

[LOGIC]:
exists x0
    with domain(x0.a: [minimum_a, maximum_a])
    => target == witness_score
    using Z3
"""


def build_demo_artifacts(directory: Path) -> tuple[Path, Path]:
    """Build the tiny public-API example without repository-local imports."""

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


def run_verification(
    specification: str | Path,
    *,
    model: str | Path | None = None,
    dataset: str | Path | None = None,
    json_output: str | Path | None = None,
) -> VerificationSession:
    """Run a Toetra policy using only the public user-facing runtime API."""

    session = verify(
        specification,
        model=model,
        dataset=dataset,
    )
    session.print()

    if json_output is not None:
        output = session.write_json(json_output)
        print(f"\nJSON report written to: {output}")

    return session


def run_self_contained_demo(
    *,
    json_output: str | Path | None = None,
) -> VerificationSession:
    """Run the user-script example without requiring pre-existing artifacts."""

    with TemporaryDirectory(prefix="toetra-user-demo-") as raw_directory:
        model_path, dataset_path = build_demo_artifacts(Path(raw_directory))
        return run_verification(
            DEMO_POLICY,
            model=model_path,
            dataset=dataset_path,
            json_output=json_output,
        )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify an ML model against a Toetra specification.",
    )
    parser.add_argument(
        "specification",
        nargs="?",
        type=Path,
        help="Path to the .toetra file. Omit it when using --demo.",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help=(
            "Run a self-contained example that trains a temporary affine model "
            "and verifies an embedded Toetra policy."
        ),
    )
    parser.add_argument(
        "--model",
        type=Path,
        help=(
            "Serialized model path. When omitted, Toetra resolves the model "
            "declared in the specification header relative to the .toetra file."
        ),
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        help="Optional reference dataset used to infer feature and target dtypes.",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        help="Optional path for the versioned JSON report collection.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.demo:
        if args.specification is not None:
            parser.error(
                "the specification positional argument cannot be used with --demo"
            )
        if args.model is not None or args.dataset is not None:
            parser.error("--model and --dataset cannot be used with --demo")
        session = run_self_contained_demo(json_output=args.json_output)
        return session.exit_code

    if args.specification is None:
        parser.error("a specification path is required unless --demo is used")

    try:
        session = run_verification(
            args.specification,
            model=args.model,
            dataset=args.dataset,
            json_output=args.json_output,
        )
    except (FileNotFoundError, VerificationConfigurationError) as error:
        parser.error(str(error))

    return session.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
