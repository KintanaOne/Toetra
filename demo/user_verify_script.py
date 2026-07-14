from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
from tempfile import TemporaryDirectory

from demo.affine_specification_constants_z3 import build_demo_artifacts
from dsl.runtime import VerificationConfigurationError, VerificationSession, verify

DEMO_SPEC_PATH = Path(__file__).with_name("user_verify_policy.forml")


def run_verification(
    specification: str | Path,
    *,
    model: str | Path | None = None,
    dataset: str | Path | None = None,
    json_output: str | Path | None = None,
) -> VerificationSession:
    """Run a FORML policy using only the public user-facing runtime API."""

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

    with TemporaryDirectory(prefix="forml-user-demo-") as raw_directory:
        model_path, dataset_path = build_demo_artifacts(Path(raw_directory))
        return run_verification(
            DEMO_SPEC_PATH,
            model=model_path,
            dataset=dataset_path,
            json_output=json_output,
        )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify an ML model against a FORML specification.",
    )
    parser.add_argument(
        "specification",
        nargs="?",
        type=Path,
        help="Path to the .forml file. Omit it when using --demo.",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help=(
            "Run a self-contained example that trains a temporary affine model "
            "and uses demo/user_verify_policy.forml."
        ),
    )
    parser.add_argument(
        "--model",
        type=Path,
        help=(
            "Serialized model path. When omitted, FORML resolves the model "
            "declared in the specification header relative to the .forml file."
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
