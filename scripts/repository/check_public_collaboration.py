"""Validate public collaboration files and untrusted pull-request workflows."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable

EXPECTED_PUBLIC_FILES = (
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/ISSUE_TEMPLATE/documentation.yml",
    ".github/ISSUE_TEMPLATE/post_v1_proposal.yml",
    ".github/dependabot.yml",
    ".github/pull_request_template.md",
    ".github/workflows/ci.yml",
    "COMMERCIAL_LICENSE.md",
    "CONTRIBUTING.md",
    "COPYRIGHT.md",
    "SECURITY.md",
    "docs/development/public-collaboration-and-workflows.md",
)

REQUIRED_MARKERS = {
    "CONTRIBUTING.md": (
        "make ci",
        "make release-check",
        "SECURITY.md",
        "PolyForm Noncommercial 1.0.0",
        "explicit contributor agreement",
        "COMMERCIAL_LICENSE.md",
        "P28",
        "P29",
    ),
    "COMMERCIAL_LICENSE.md": (
        "PolyForm Noncommercial License 1.0.0",
        "separate written commercial",
        "hosted or managed-service use",
        "KintanaOne@proton.me",
        "THIRD_PARTY.md",
    ),
    "COPYRIGHT.md": (
        "Copyright © 2025–2026 Tina RANDRIANARIJAONA-DUBIN",
        "declared copyright holder and licensor",
        "THIRD_PARTY.md",
        "INPI e-Soleau",
    ),
    "SECURITY.md": (
        "1.0.0rc3",
        "Do not open a public issue",
        "private vulnerability reporting",
        "KintanaOne@proton.me",
    ),
    ".github/ISSUE_TEMPLATE/config.yml": (
        "blank_issues_enabled: false",
        "https://github.com/KintanaOne/Toetra/security/policy",
    ),
    ".github/ISSUE_TEMPLATE/bug_report.yml": (
        "name: Bug report",
        "Minimal reproduction",
        "SECURITY.md",
        "required: true",
    ),
    ".github/ISSUE_TEMPLATE/documentation.yml": (
        "name: Documentation issue",
        "Page or location",
        "required: true",
    ),
    ".github/ISSUE_TEMPLATE/post_v1_proposal.yml": (
        "name: Post-V1 proposal",
        "outside the frozen P27",
        "required: true",
    ),
    ".github/pull_request_template.md": (
        "make ci",
        "Verification or numeric guarantee changed",
        "required contributor agreement",
        "commercial relicensing rights",
        "P28 CLI",
        "P29 stable release",
    ),
    ".github/dependabot.yml": (
        'package-ecosystem: "github-actions"',
        'directory: "/"',
        'interval: "weekly"',
    ),
    "docs/development/public-collaboration-and-workflows.md": (
        "make public-collaboration-check",
        "Default workflow permissions are read-only",
        "Private vulnerability reporting is enabled",
        "explicit contributor agreement",
        "outside code and documentation pull requests are not",
        "pull_request_target",
    ),
}

FORBIDDEN_WORKFLOW_MARKERS = (
    "pull_request_target:",
    "workflow_run:",
    "secrets.",
    "twine upload",
    "gh release create",
    "pypa/gh-action-pypi-publish",
)

ACTION_USE = re.compile(
    r"^\s*uses:\s*(?P<target>[^@\s]+)@(?P<reference>[^\s#]+)"
    r"(?:\s+#\s*(?P<label>.+))?$",
    re.MULTILINE,
)
WRITE_PERMISSION = re.compile(
    r"^\s*(?:permissions\s*:\s*write-all|[a-z][a-z-]*\s*:\s*write)\s*$",
    re.MULTILINE,
)


class PublicCollaborationError(RuntimeError):
    """Raised when public collaboration or workflow controls are incomplete."""


def _workflow_errors(path: Path, source: str) -> list[str]:
    relative = path.as_posix()
    errors: list[str] = []

    if not re.search(r"^permissions:\s*\n  contents:\s*read\s*$", source, re.MULTILINE):
        errors.append(f"{relative} does not declare top-level contents: read")
    if WRITE_PERMISSION.search(source):
        errors.append(f"{relative} grants a write-capable workflow permission")
    if "timeout-minutes:" not in source:
        errors.append(f"{relative} does not bound job execution time")

    for marker in FORBIDDEN_WORKFLOW_MARKERS:
        if marker in source:
            errors.append(f"{relative} contains forbidden workflow marker {marker!r}")

    uses_lines = tuple(
        line.strip() for line in source.splitlines() if line.strip().startswith("uses:")
    )
    matches = tuple(ACTION_USE.finditer(source))
    if len(matches) != len(uses_lines):
        errors.append(f"{relative} contains an unparseable or local action reference")

    for match in matches:
        target = match.group("target")
        reference = match.group("reference")
        label = (match.group("label") or "").strip()
        if not re.fullmatch(r"[0-9a-f]{40}", reference):
            errors.append(
                f"{relative} action {target!r} is not pinned to a full commit SHA"
            )
        if not re.fullmatch(r"v\d+(?:\.\d+){0,2}", label):
            errors.append(
                f"{relative} action {target!r} has no reviewed version comment"
            )

    if "actions/checkout@" in source and "persist-credentials: false" not in source:
        errors.append(f"{relative} allows checkout credentials to persist")

    return errors


def public_collaboration_errors(repository: Path) -> tuple[str, ...]:
    """Return every source-controlled P27.3 collaboration violation."""

    repository = repository.resolve()
    errors: list[str] = []

    for raw_path in EXPECTED_PUBLIC_FILES:
        if not (repository / raw_path).is_file():
            errors.append(f"Missing public collaboration file: {raw_path}")

    for raw_path, markers in REQUIRED_MARKERS.items():
        path = repository / raw_path
        if not path.is_file():
            continue
        source = path.read_text(encoding="utf-8")
        missing = tuple(marker for marker in markers if marker not in source)
        if missing:
            errors.append(
                f"{raw_path} is missing required markers: {', '.join(missing)}"
            )

    workflows = tuple(
        sorted(
            (
                *repository.glob(".github/workflows/*.yml"),
                *repository.glob(".github/workflows/*.yaml"),
            )
        )
    )
    if not workflows:
        errors.append("No GitHub Actions workflow is present")
    for workflow in workflows:
        errors.extend(
            _workflow_errors(
                workflow.relative_to(repository),
                workflow.read_text(encoding="utf-8"),
            )
        )

    return tuple(errors)


def validate_public_collaboration(repository: Path) -> None:
    """Raise when P27.3 collaboration or workflow controls are incomplete."""

    errors = public_collaboration_errors(repository)
    if errors:
        details = "\n".join(f"- {error}" for error in errors)
        raise PublicCollaborationError(
            "Toetra public collaboration violations:\n" + details
        )


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
        validate_public_collaboration(arguments.repository)
    except PublicCollaborationError as error:
        print(error)
        return 1
    print("Toetra public collaboration contract: valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
