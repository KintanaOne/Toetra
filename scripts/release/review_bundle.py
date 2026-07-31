"""Create deterministic, complete Toetra review bundles."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

from .distribution import DEFAULT_SOURCE_DATE_EPOCH, sha256_file

EXCLUDED_PARTS = {
    ".git",
    ".hypothesis",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "site",
}
EXCLUDED_PREFIXES = ("context/", "_meta/")
EXCLUDED_SUFFIXES = (".pyc", ".pyo", ".joblib", ".pkl")
SENSITIVE_FILE_NAMES = frozenset(
    {
        ".env",
        ".npmrc",
        ".pypirc",
        "credentials",
        "credentials.json",
        "id_dsa",
        "id_ed25519",
        "id_rsa",
        "secrets.json",
    }
)
SENSITIVE_SUFFIXES = frozenset({".key", ".p12", ".pem", ".pfx"})
CRITICAL_PATHS = (
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/ISSUE_TEMPLATE/documentation.yml",
    ".github/ISSUE_TEMPLATE/post_v1_proposal.yml",
    ".github/dependabot.yml",
    ".github/pull_request_template.md",
    ".github/workflows/ci.yml",
    "CHANGELOG.md",
    "COMMERCIAL_LICENSE.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "Makefile",
    "README.md",
    "SECURITY.md",
    "THIRD_PARTY.md",
    "pyproject.toml",
    "docs/adr/ADR-0030-separate-public-exposure-cli-and-stable-release.md",
    "docs/adr/ADR-0031-noncommercial-and-commercial-licensing.md",
    "docs/contracts/public-repository-readiness.md",
    "docs/contracts/repository-contract.md",
    "docs/development/public-repository-audit.md",
    "docs/development/public-collaboration-and-workflows.md",
    "docs/development/public-exposure-runbook.md",
    "docs/development/outside-in-rehearsal.md",
    "scripts/release/check_public_surfaces.py",
    "scripts/release/check_outside_in.py",
    "scripts/repository/check_public_collaboration.py",
    "scripts/repository/check_public_exposure.py",
    "scripts/repository/check_repository_contract.py",
    "src/toetra/__init__.py",
    "src/toetra/examples/credit_risk_policy.toetra",
    "src/toetra/_language/grammar/toetra_grammar.ebnf",
    "src/toetra/_language/grammar/toetra_grammar.lark",
    "demo/regression/credit_risk_validation.ipynb",
    "demo/classification/cleveland/README.md",
    "demo/classification/cleveland/data/heart-disease-cleveland.csv",
    "tests/fixtures/model_bridge/classification.csv",
    "tests/fixtures/model_bridge/regression.csv",
)


class ReviewBundleError(RuntimeError):
    """Raised when a review bundle cannot satisfy its source contract."""


@dataclass(frozen=True, slots=True)
class ReviewBundle:
    path: Path
    manifest: dict[str, object]

    @property
    def sha256(self) -> str:
        return sha256_file(self.path)


def _repository_epoch(repository: Path) -> int:
    raw = os.environ.get("SOURCE_DATE_EPOCH")
    if raw:
        try:
            return int(raw)
        except ValueError as exc:
            raise ReviewBundleError("SOURCE_DATE_EPOCH must be an integer.") from exc
    try:
        completed = subprocess.run(
            ["git", "log", "-1", "--format=%ct"],
            cwd=repository,
            check=True,
            capture_output=True,
            text=True,
        )
        return int(completed.stdout.strip())
    except (OSError, subprocess.CalledProcessError, ValueError):
        return DEFAULT_SOURCE_DATE_EPOCH


def _tracked_and_untracked_files(repository: Path) -> tuple[Path, ...]:
    try:
        completed = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=repository,
            check=True,
            capture_output=True,
        )
        raw_paths = completed.stdout.split(b"\0")
        paths = [repository / os.fsdecode(raw) for raw in raw_paths if raw]
    except (OSError, subprocess.CalledProcessError):
        paths = [path for path in repository.rglob("*") if path.is_file()]
    return tuple(
        sorted(paths, key=lambda path: path.relative_to(repository).as_posix())
    )


def _is_sensitive(relative: Path) -> bool:
    name = relative.name.lower()
    return (
        name in SENSITIVE_FILE_NAMES
        or name.startswith(".env.")
        or relative.suffix.lower() in SENSITIVE_SUFFIXES
    )


def _included(repository: Path, path: Path) -> bool:
    relative = path.relative_to(repository)
    posix = relative.as_posix()
    if any(part in EXCLUDED_PARTS for part in relative.parts):
        return False
    if posix.startswith(EXCLUDED_PREFIXES):
        return False
    if posix.endswith(EXCLUDED_SUFFIXES):
        return False
    if _is_sensitive(relative):
        return False
    return path.is_file() and not path.is_symlink()


def collect_review_files(repository: Path) -> tuple[Path, ...]:
    """Collect source files in deterministic path order."""

    repository = repository.resolve()
    return tuple(
        path
        for path in _tracked_and_untracked_files(repository)
        if _included(repository, path)
    )


def _missing_critical_paths(repository: Path) -> list[str]:
    return [path for path in CRITICAL_PATHS if not (repository / path).is_file()]


def _file_entry(repository: Path, path: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(repository).as_posix(),
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def _git_metadata(repository: Path) -> dict[str, object]:
    def run(*arguments: str) -> str | None:
        try:
            completed = subprocess.run(
                ["git", *arguments],
                cwd=repository,
                check=True,
                capture_output=True,
                text=True,
            )
            return completed.stdout.strip() or None
        except (OSError, subprocess.CalledProcessError):
            return None

    status = run("status", "--short")
    return {
        "commit": run("rev-parse", "HEAD"),
        "branch": run("branch", "--show-current"),
        "dirty": bool(status),
        "status": status.splitlines() if status else [],
    }


def _zip_datetime(epoch: int) -> tuple[int, int, int, int, int, int]:
    moment = datetime.fromtimestamp(max(epoch, 315_532_800), tz=timezone.utc)
    second = moment.second - (moment.second % 2)
    return (moment.year, moment.month, moment.day, moment.hour, moment.minute, second)


def _writestr(
    archive: zipfile.ZipFile,
    name: str,
    payload: bytes,
    *,
    epoch: int,
) -> None:
    pure = PurePosixPath(name)
    if pure.is_absolute() or ".." in pure.parts:
        raise ReviewBundleError(f"Unsafe bundle path: {name!r}")
    info = zipfile.ZipInfo(name, date_time=_zip_datetime(epoch))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    info.create_system = 3
    archive.writestr(info, payload, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def build_review_bundle(
    repository: Path,
    output: Path,
    *,
    require_complete: bool = True,
) -> ReviewBundle:
    """Create one deterministic source snapshot and embedded manifest."""

    repository = repository.resolve()
    output = output.resolve()
    missing = _missing_critical_paths(repository)
    if missing and require_complete:
        raise ReviewBundleError(
            "Review bundle is incomplete; missing critical paths:\n  - "
            + "\n  - ".join(missing)
        )

    files = collect_review_files(repository)
    entries = [_file_entry(repository, path) for path in files]
    epoch = _repository_epoch(repository)
    manifest: dict[str, object] = {
        "schema_version": 2,
        "bundle_kind": "toetra_review_source_snapshot",
        "source_date_epoch": epoch,
        "created_at_utc": datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat(),
        "repository_root_name": repository.name,
        "file_count": len(entries),
        "total_size_bytes": sum(path.stat().st_size for path in files),
        "critical_paths": list(CRITICAL_PATHS),
        "missing_critical_paths": missing,
        "git": _git_metadata(repository),
        "files": entries,
    }
    manifest_payload = (
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    with zipfile.ZipFile(temporary, mode="w") as archive:
        for path in files:
            relative = path.relative_to(repository).as_posix()
            _writestr(archive, relative, path.read_bytes(), epoch=epoch)
        _writestr(archive, "_meta/manifest.json", manifest_payload, epoch=epoch)
    temporary.replace(output)
    return ReviewBundle(path=output, manifest=manifest)


def check_review_bundle_reproducibility(repository: Path) -> str:
    """Build the same review bundle twice and compare byte hashes."""

    with tempfile.TemporaryDirectory(prefix="toetra-bundle-repro-") as raw_directory:
        directory = Path(raw_directory)
        first = build_review_bundle(repository, directory / "first.zip")
        second = build_review_bundle(repository, directory / "second.zip")
        if first.sha256 != second.sha256:
            raise ReviewBundleError(
                "Review bundle is not byte-reproducible: "
                f"first={first.sha256}, second={second.sha256}."
            )
        return first.sha256
