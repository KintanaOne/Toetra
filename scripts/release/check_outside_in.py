"""Rehearse the complete public Toetra journey from an exact clean clone."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import tempfile
import venv
from pathlib import Path
from typing import Iterable, Sequence

PUBLIC_JOURNEY_GATES = (
    "ci",
    "demo-check",
    "release-check",
    "review-bundle-check",
)
EXPECTED_QUICKSTART_STATUSES = ("PROVED", "WITNESS")
STATUS_LINE = re.compile(
    r"^Status\s*:.*\b(PROVED|COUNTEREXAMPLE|WITNESS|NO_WITNESS|UNKNOWN)\b",
    re.MULTILINE,
)


class OutsideInCheckError(RuntimeError):
    """Raised when the public journey cannot be reproduced from a clean clone."""


def _run(
    command: Sequence[str],
    *,
    cwd: Path,
    environment: dict[str, str] | None = None,
    capture_output: bool = False,
) -> subprocess.CompletedProcess[str]:
    print(f"$ {' '.join(command)}", flush=True)
    try:
        return subprocess.run(
            list(command),
            cwd=cwd,
            env=environment,
            check=True,
            capture_output=capture_output,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise OutsideInCheckError(
            f"Public journey command failed: {' '.join(command)}"
        ) from error


def _git_text(repository: Path, *arguments: str) -> str:
    completed = _run(
        ("git", *arguments),
        cwd=repository,
        capture_output=True,
    )
    return completed.stdout.strip()


def candidate_commit(repository: Path) -> str:
    """Return the exact clean, non-shallow source commit to rehearse."""

    repository = repository.resolve()
    if not (repository / ".git").exists():
        raise OutsideInCheckError(
            "The outside-in rehearsal requires a complete Git checkout."
        )
    if _git_text(repository, "rev-parse", "--is-shallow-repository") == "true":
        raise OutsideInCheckError(
            "The outside-in rehearsal requires a non-shallow canonical clone."
        )
    status = _git_text(repository, "status", "--porcelain", "--untracked-files=all")
    if status:
        raise OutsideInCheckError(
            "Commit or remove pending files before the outside-in rehearsal."
        )
    return _git_text(repository, "rev-parse", "HEAD")


def clone_candidate(repository: Path, destination: Path, commit: str) -> None:
    """Clone and detach exactly the selected source commit."""

    if destination.exists():
        raise OutsideInCheckError(
            f"Outside-in destination already exists: {destination}"
        )
    _run(
        (
            "git",
            "clone",
            "--quiet",
            "--no-local",
            "--no-checkout",
            str(repository.resolve()),
            str(destination),
        ),
        cwd=repository.parent,
    )
    _run(
        ("git", "checkout", "--quiet", "--detach", commit),
        cwd=destination,
    )
    cloned_commit = _git_text(destination, "rev-parse", "HEAD")
    if cloned_commit != commit:
        raise OutsideInCheckError(
            f"Cloned commit differs from candidate: {cloned_commit} != {commit}"
        )
    if _git_text(destination, "status", "--porcelain", "--untracked-files=all"):
        raise OutsideInCheckError("The candidate clone is not initially clean.")


def validate_quickstart_output(source: str) -> None:
    """Require the two conclusions promised by the public README."""

    statuses = tuple(STATUS_LINE.findall(source))
    if statuses != EXPECTED_QUICKSTART_STATUSES:
        raise OutsideInCheckError(
            "README quickstart conclusions differ from the public promise: "
            f"expected={EXPECTED_QUICKSTART_STATUSES}, found={statuses}"
        )


def _venv_python(directory: Path) -> Path:
    if os.name == "nt":
        return directory / "Scripts" / "python.exe"
    return directory / "bin" / "python"


def _environment_for(python: Path) -> dict[str, str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment.pop("PYTHONSAFEPATH", None)
    environment["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    environment["PATH"] = str(python.parent) + os.pathsep + environment.get("PATH", "")
    return environment


def run_public_journey(repository: Path) -> str:
    """Run the documented first use and all durable gates from a fresh clone."""

    repository = repository.resolve()
    commit = candidate_commit(repository)
    with tempfile.TemporaryDirectory(prefix="toetra-outside-in-") as raw_directory:
        root = Path(raw_directory)
        checkout = root / "Toetra"
        environment_directory = root / "venv"
        clone_candidate(repository, checkout, commit)

        venv.EnvBuilder(with_pip=True, clear=True).create(environment_directory)
        python = _venv_python(environment_directory)
        environment = _environment_for(python)

        _run(
            (str(python), "-m", "pip", "install", "."),
            cwd=checkout,
            environment=environment,
        )
        _run(
            (
                str(python),
                "-c",
                "from toetra import verify; print('Toetra import: OK')",
            ),
            cwd=checkout,
            environment=environment,
        )
        quickstart = _run(
            (str(python), "-m", "demo.quickstart.verify_model", "--demo"),
            cwd=checkout,
            environment=environment,
            capture_output=True,
        )
        print(quickstart.stdout, end="")
        validate_quickstart_output(quickstart.stdout)

        _run(
            (str(python), "-m", "pip", "install", "-e", ".[dev,docs]"),
            cwd=checkout,
            environment=environment,
        )
        for target in PUBLIC_JOURNEY_GATES:
            _run(("make", target), cwd=checkout, environment=environment)

        final_status = _git_text(
            checkout,
            "status",
            "--porcelain",
            "--untracked-files=all",
        )
        if final_status:
            raise OutsideInCheckError(
                "The public journey left tracked or untracked files in the clone."
            )

    return commit


def _repository_from_script() -> Path:
    return Path(__file__).resolve().parents[2]


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "repository",
        nargs="?",
        type=Path,
        default=_repository_from_script(),
    )
    arguments = parser.parse_args(argv)
    try:
        commit = run_public_journey(arguments.repository)
    except OutsideInCheckError as error:
        print(f"Toetra outside-in rehearsal failed: {error}")
        return 1
    print(f"Toetra outside-in rehearsal passed for commit {commit}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
