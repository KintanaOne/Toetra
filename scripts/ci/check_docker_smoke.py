"""Run the complete CLI smoke scenario inside a Docker image."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True)
    args = parser.parse_args()
    repository = Path(__file__).resolve().parents[2]

    command = [
        "docker",
        "run",
        "--rm",
        "--pull=never",
        "--mount",
        f"type=bind,source={repository.as_posix()},target=/checks,readonly",
        "--entrypoint",
        "python",
        args.image,
        "/checks/scripts/ci/check_cli_smoke.py",
    ]
    try:
        completed = subprocess.run(command, cwd=repository, check=False)
    except OSError as error:
        parser.exit(1, f"Cannot start Docker: {error}\n")
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
