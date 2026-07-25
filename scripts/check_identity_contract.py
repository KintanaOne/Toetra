"""Reject unapproved references to the superseded project identity."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY_IDENTITY_PATTERN = re.compile(r"FORML|(?<![a-z])forml(?![a-z])|\.forml")
TEXT_SUFFIXES = frozenset(
    {
        ".cfg",
        ".ebnf",
        ".ini",
        ".ipynb",
        ".json",
        ".lark",
        ".md",
        ".py",
        ".toml",
        ".txt",
        ".yaml",
        ".yml",
    }
)
TEXT_FILE_NAMES = frozenset({".gitignore", "Makefile", "MANIFEST.in"})
EXCLUDED_PARTS = frozenset(
    {
        ".git",
        ".hypothesis",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "_meta",
        "build",
        "context",
        "dist",
        "site",
    }
)

# Historical records and explicit compatibility-rejection tests may retain the
# former identity. Expanding this set requires review because the gate exists to
# prevent silent dual-brand drift.
LEGACY_IDENTITY_ALLOWLIST = frozenset(
    {
        "CHANGELOG.md",
        "docs/adr/ADR-0027-adopt-toetra-as-canonical-identity.md",
        "docs/roadmap/toetra-identity-migration-roadmap.md",
        "dsl/runtime/api.py",
        "scripts/check_installed_distribution.py",
        "scripts/release/distribution.py",
        "test/fixtures/reporting/golden/verification_report_v1.json",
        "test/fixtures/reporting/golden/verification_report_v2.json",
        "test/fixtures/reporting/golden/verification_report_v3.json",
        "test/fixtures/reporting/golden/verification_report_v4.json",
        "test/fixtures/reporting/golden/verification_report_v5.json",
        "test/unit/parser/test_toetra_language_identity.py",
        "test/unit/provenance/test_builder.py",
        "test/unit/release/test_distribution_contract.py",
        "test/unit/release/test_identity_contract.py",
        "test/unit/release/test_release_configuration.py",
        "test/unit/repository/test_repository_hygiene.py",
        "test/unit/reporting/test_classification_evaluations.py",
        "test/unit/reporting/test_json_renderer.py",
        "test/unit/runtime/test_replay.py",
        "test/unit/runtime/test_verify_api.py",
    }
)


class IdentityContractError(RuntimeError):
    """Raised when an unapproved former-identity reference is found."""


@dataclass(frozen=True, slots=True)
class IdentityViolation:
    path: str
    line_number: int
    line: str


def _repository_files(repository: Path) -> tuple[Path, ...]:
    try:
        completed = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=repository,
            check=True,
            capture_output=True,
        )
        raw_paths = completed.stdout.split(b"\0")
        paths = tuple(repository / os.fsdecode(raw) for raw in raw_paths if raw)
    except (OSError, subprocess.CalledProcessError):
        paths = tuple(path for path in repository.rglob("*") if path.is_file())
    return tuple(
        sorted(paths, key=lambda path: path.relative_to(repository).as_posix())
    )


def _is_text_candidate(path: Path) -> bool:
    return path.name in TEXT_FILE_NAMES or path.suffix.lower() in TEXT_SUFFIXES


def collect_identity_violations(
    repository: Path = ROOT,
) -> tuple[IdentityViolation, ...]:
    """Return unapproved former-identity references in source-controlled text."""

    repository = repository.resolve()
    violations: list[IdentityViolation] = []
    for path in _repository_files(repository):
        if (
            not path.is_file()
            or any(
                part in EXCLUDED_PARTS for part in path.relative_to(repository).parts
            )
            or not _is_text_candidate(path)
        ):
            continue
        relative = path.relative_to(repository).as_posix()
        if relative == "scripts/check_identity_contract.py":
            continue
        if relative in LEGACY_IDENTITY_ALLOWLIST:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(lines, start=1):
            if LEGACY_IDENTITY_PATTERN.search(line):
                violations.append(
                    IdentityViolation(
                        path=relative,
                        line_number=line_number,
                        line=line.strip(),
                    )
                )
    return tuple(violations)


def check_identity_contract(repository: Path = ROOT) -> None:
    """Fail when the source tree reintroduces an unapproved old identity."""

    violations = collect_identity_violations(repository)
    if not violations:
        return
    details = "\n".join(
        f"  - {item.path}:{item.line_number}: {item.line}" for item in violations
    )
    raise IdentityContractError(
        "Unapproved former-identity references found:\n" + details
    )


def main() -> int:
    try:
        check_identity_contract()
    except IdentityContractError as error:
        print(f"Toetra identity contract failed: {error}", file=sys.stderr)
        return 1
    print("Toetra identity contract: valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
