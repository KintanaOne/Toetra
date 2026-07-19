"""CLI for complete and reproducible FORML review bundles."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    repository_root = Path(__file__).resolve().parents[1]
    if str(repository_root) not in sys.path:
        sys.path.insert(0, str(repository_root))
    from scripts.release.review_bundle import (
        build_review_bundle,
        check_review_bundle_reproducibility,
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output", type=Path, default=Path("dist/forml_review_bundle.zip")
    )
    parser.add_argument("--check-reproducible", action="store_true")
    parser.add_argument("--allow-incomplete", action="store_true")
    arguments = parser.parse_args()

    if arguments.check_reproducible:
        digest = check_review_bundle_reproducibility(arguments.repository)
        print(f"Review bundle reproducible: {digest}")
        return 0

    bundle = build_review_bundle(
        arguments.repository,
        arguments.output,
        require_complete=not arguments.allow_incomplete,
    )
    print(f"Review bundle created: {bundle.path}")
    print(f"SHA-256: {bundle.sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
