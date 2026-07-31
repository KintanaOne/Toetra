from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts.release.check_outside_in import (
    EXPECTED_QUICKSTART_STATUSES,
    OutsideInCheckError,
    candidate_commit,
    clone_candidate,
    validate_quickstart_output,
)


def _git(repository: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _repository(tmp_path: Path) -> Path:
    repository = tmp_path / "source"
    repository.mkdir()
    _git(repository, "init")
    _git(repository, "config", "user.name", "Outside In Test")
    _git(repository, "config", "user.email", "outside-in@example.invalid")
    (repository / "README.md").write_text("candidate\n", encoding="utf-8")
    _git(repository, "add", "README.md")
    _git(repository, "commit", "-m", "candidate")
    return repository


def test_candidate_clone_is_exact_detached_and_clean(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    commit = candidate_commit(repository)
    checkout = tmp_path / "checkout"

    clone_candidate(repository, checkout, commit)

    assert _git(checkout, "rev-parse", "HEAD") == commit
    assert _git(checkout, "status", "--porcelain", "--untracked-files=all") == ""
    assert _git(checkout, "branch", "--show-current") == ""


def test_candidate_commit_rejects_pending_files(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    (repository / "private-note.txt").write_text("pending\n", encoding="utf-8")

    with pytest.raises(OutsideInCheckError, match="pending files"):
        candidate_commit(repository)


def test_quickstart_output_requires_the_public_conclusion_order() -> None:
    output = "\n".join(
        (
            "Status        : ✓ PROVED",
            "Status        : ✓ WITNESS",
        )
    )

    validate_quickstart_output(output)
    assert EXPECTED_QUICKSTART_STATUSES == ("PROVED", "WITNESS")

    with pytest.raises(OutsideInCheckError, match="conclusions differ"):
        validate_quickstart_output("Status        : ✗ COUNTEREXAMPLE\n")
