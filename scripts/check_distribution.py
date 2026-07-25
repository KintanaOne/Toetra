"""CLI for validating Toetra wheel and sdist contents."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    repository_root = Path(__file__).resolve().parents[1]
    if str(repository_root) not in sys.path:
        sys.path.insert(0, str(repository_root))
    from scripts.release.distribution import check_distribution_directory

    parser = argparse.ArgumentParser()
    parser.add_argument("directory", nargs="?", type=Path, default=Path("dist"))
    arguments = parser.parse_args()
    artifacts = check_distribution_directory(arguments.directory)
    print(
        f"Distribution contract valid: {artifacts.wheel.name}, {artifacts.sdist.name}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
