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


def _allow(*fragments: str) -> tuple[re.Pattern[str], ...]:
    return tuple(re.compile(re.escape(fragment)) for fragment in fragments)


# Every retained historical or rejection reference is allowed by line content,
# not merely by filename. Adding a new former-identity reference to one of these
# files therefore still fails the repository gate unless its reason is reviewed.
LEGACY_IDENTITY_ALLOWANCES: dict[str, tuple[re.Pattern[str], ...]] = {
    "CHANGELOG.md": _allow(
        "legacy `forml` import namespace and `.forml` extension",
    ),
    "docs/adr/ADR-0027-adopt-toetra-as-canonical-identity.md": _allow(
        "name `FORML` was found to",
        "language name and `.forml` extension",
        "stable `forml` distribution has been released",
        "public `forml` import alias",
        "`.forml` compatibility extension",
        "mixed FORML/Toetra identity",
        "Keep FORML as the product",
        "Keep `.forml` as the language extension",
    ),
    "docs/roadmap/toetra-identity-migration-roadmap.md": _allow(
        "identity from FORML to Toetra",
        "`forml` package facade",
        "remove `forml` from package discovery",
        "`import forml` is not supported",
        "rename `.forml` specifications",
        "`parse_forml_code`",
        "code fences from `forml` to `toetra`",
        "`forml.*` JSON schema",
        "unapproved `FORML`, `forml` or `.forml`",
        "rg -n 'FORML|forml|\\.forml'",
    ),
    "src/toetra/_runtime/api.py": _allow(
        'candidate.suffix.lower() == ".forml"',
        "Legacy '.forml' specifications are not supported",
    ),
    "scripts/check_installed_distribution.py": _allow(
        'find_spec("forml") is None',
    ),
    "scripts/release/distribution.py": _allow(
        'FORBIDDEN_TOP_LEVEL_PACKAGES = ("forml", "dsl", "model")',
    ),
    "test/fixtures/reporting/golden/verification_report_v1.json": _allow(
        '"schema": "forml.verification-report"',
    ),
    "test/fixtures/reporting/golden/verification_report_v2.json": _allow(
        '"schema": "forml.verification-report"',
    ),
    "test/fixtures/reporting/golden/verification_report_v3.json": _allow(
        '"schema": "forml.verification-report"',
    ),
    "test/fixtures/reporting/golden/verification_report_v4.json": _allow(
        '"schema": "forml.verification-report"',
    ),
    "test/fixtures/reporting/golden/verification_report_v5.json": _allow(
        '"schema": "forml.verification-report"',
        '"forml_version": "1.0.0rc1"',
        '"forml_build_id": "git:abc123"',
    ),
    "test/unit/parser/test_toetra_language_identity.py": _allow(
        'hasattr(parser_module, "parse_forml_code")',
        '"forml_grammar.ebnf"',
        '"forml_grammar.lark"',
        'rglob("*.forml")',
    ),
    "test/unit/provenance/test_builder.py": _allow(
        '"forml" not in requested',
        'setenv("FORML_BUILD_ID"',
    ),
    "test/unit/release/test_distribution_contract.py": _allow(
        '"forml/__init__.py"',
        '["forml", "dsl", "model"]',
    ),
    "test/unit/release/test_identity_contract.py": _allow(
        "The FORML package accepts policy.forml.",
        "name `FORML` was found to",
    ),
    "test/unit/release/test_release_configuration.py": _allow(
        'find_spec("forml") is None',
    ),
    "test/unit/reporting/test_classification_evaluations.py": _allow(
        '"forml.verification-report"',
    ),
    "test/unit/reporting/test_json_renderer.py": _allow(
        '"forml_version" not in software',
        '"forml_build_id" not in software',
    ),
    "test/unit/repository/test_repository_hygiene.py": _allow(
        'glob("forml_review_bundle_*.zip")',
        '"/forml_review_bundle_*.zip" not in ignore_rules',
    ),
    "test/unit/runtime/test_replay.py": _allow(
        '"forml_score" not in record',
    ),
    "test/unit/runtime/test_verify_api.py": _allow(
        '"legacy.forml"',
        "legacy_forml_extension",
    ),
}


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


def _line_is_allowed(relative: str, line: str) -> bool:
    return any(
        pattern.search(line) for pattern in LEGACY_IDENTITY_ALLOWANCES.get(relative, ())
    )


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
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(lines, start=1):
            if not LEGACY_IDENTITY_PATTERN.search(line):
                continue
            if _line_is_allowed(relative, line):
                continue
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
