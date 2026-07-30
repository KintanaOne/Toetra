from __future__ import annotations

import subprocess
from pathlib import Path

from scripts.repository.check_public_exposure import (
    CLEVELAND_PATH,
    CLEVELAND_SHA256,
    audit_history,
    audit_snapshot,
)

ROOT = Path(__file__).parents[3]


def _git(repository: Path, *arguments: str) -> None:
    subprocess.run(
        ["git", *arguments],
        cwd=repository,
        check=True,
        capture_output=True,
    )


def _initialize_repository(repository: Path) -> None:
    repository.mkdir()
    _git(repository, "init")
    _git(repository, "config", "user.name", "Public Audit Test")
    _git(repository, "config", "user.email", "audit@example.invalid")


def test_current_public_snapshot_has_no_automated_blocker() -> None:
    assert audit_snapshot(ROOT) == ()


def test_cleveland_dataset_digest_is_frozen() -> None:
    import hashlib

    dataset = ROOT / CLEVELAND_PATH
    canonical_payload = dataset.read_bytes().replace(b"\r\n", b"\n")

    assert hashlib.sha256(canonical_payload).hexdigest() == CLEVELAND_SHA256


def test_snapshot_audit_reports_sensitive_filename_without_value(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repository"
    _initialize_repository(repository)
    (repository / ".env").write_text("safe placeholder\n", encoding="utf-8")
    _git(repository, "add", ".env")

    findings = audit_snapshot(repository)

    assert {(finding.rule, finding.location) for finding in findings} == {
        ("missing-third-party-asset", str(CLEVELAND_PATH)),
        ("missing-third-party-notice", "THIRD_PARTY.md"),
        (
            "unlinked-third-party-notice",
            "demo/classification/cleveland/README.md",
        ),
        ("sensitive-filename", ".env"),
    }


def test_history_audit_finds_deleted_secret_without_rendering_it(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repository"
    _initialize_repository(repository)
    secret = "gh" + "p_" + "A" * 36
    path = repository / "temporary.txt"
    path.write_text(secret + "\n", encoding="utf-8")
    _git(repository, "add", "temporary.txt")
    _git(repository, "commit", "-m", "add temporary file")
    path.unlink()
    _git(repository, "add", "-u")
    _git(repository, "commit", "-m", "remove temporary file")

    findings = audit_history(repository)
    rendered = "\n".join(finding.render() for finding in findings)

    assert any(finding.rule == "github-token" for finding in findings)
    assert secret not in rendered
