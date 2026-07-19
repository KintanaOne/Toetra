"""CLI for deterministic FORML wheel and sdist builds."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    repository_root = Path(__file__).resolve().parents[1]
    if str(repository_root) not in sys.path:
        sys.path.insert(0, str(repository_root))
    from scripts.release.distribution import build_distributions

    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=Path("dist"))
    parser.add_argument("--check-reproducible", action="store_true")
    arguments = parser.parse_args()

    artifacts = build_distributions(
        arguments.repository,
        arguments.output,
        check_reproducible=arguments.check_reproducible,
    )
    for name, digest in artifacts.sha256().items():
        print(f"{digest}  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
