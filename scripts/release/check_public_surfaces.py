"""Verify Toetra's public GitHub surfaces without authentication."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import zipfile
from collections.abc import Callable, Iterable
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPOSITORY_URL = "https://github.com/KintanaOne/Toetra"
API_URL = "https://api.github.com/repos/KintanaOne/Toetra"
DOCUMENTATION_URL = "https://kintanaone.github.io/Toetra/"
DEFAULT_BRANCH = "main"
COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}")
EXPECTED_LICENSE = "PolyForm-Noncommercial-1.0.0"
EXPECTED_COPYRIGHT_HOLDER = "Tina RANDRIANARIJAONA-DUBIN"
EXPECTED_COPYRIGHT_YEARS = "2025-2026"
UNASSERTED_LICENSE_IDS = (None, "NOASSERTION")

RAW_SURFACES = {
    "README": ("README.md", ("# Toetra", "1.0.0rc3")),
    "license": (
        "LICENSE",
        (
            "PolyForm Noncommercial License 1.0.0",
            "Any noncommercial purpose is a permitted purpose.",
        ),
    ),
    "commercial licensing": (
        "COMMERCIAL_LICENSE.md",
        ("separate written commercial", "KintanaOne@proton.me"),
    ),
    "copyright notice": (
        "COPYRIGHT.md",
        (
            "Copyright © 2025–2026 Tina RANDRIANARIJAONA-DUBIN",
            "declared copyright holder and licensor",
            "THIRD_PARTY.md",
        ),
    ),
    "contribution guide": ("CONTRIBUTING.md", ("# Contributing", "make ci")),
    "security policy": ("SECURITY.md", ("# Security", "1.0.0rc3")),
    "bug-report form": (
        ".github/ISSUE_TEMPLATE/bug_report.yml",
        ("name: Bug report", "Minimal reproduction"),
    ),
}
HTML_SURFACES = {
    "issues": (f"{REPOSITORY_URL}/issues", ("Toetra",)),
    "security policy": (f"{REPOSITORY_URL}/security/policy", ("Security",)),
    "documentation": (DOCUMENTATION_URL, ("Toetra",)),
}


class PublicSurfaceCheckError(RuntimeError):
    """Raised when the anonymous public-exposure proof is incomplete."""


Fetcher = Callable[[str, str], bytes]
RemoteReader = Callable[[str], tuple[str, str]]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fetch(url: str, accept: str) -> bytes:
    request = Request(
        url,
        headers={
            "Accept": accept,
            "User-Agent": "Toetra-P27-public-surface-check/1",
        },
    )
    try:
        with urlopen(request, timeout=20) as response:
            status = response.getcode()
            payload = response.read()
    except (HTTPError, URLError, TimeoutError) as error:
        raise PublicSurfaceCheckError(
            f"Anonymous request failed for {url}: {error}"
        ) from error
    if status != 200:
        raise PublicSurfaceCheckError(
            f"Anonymous request returned HTTP {status} for {url}"
        )
    return payload


def _anonymous_remote_head(repository_url: str) -> tuple[str, str]:
    environment = os.environ.copy()
    environment.update(
        {
            "GCM_INTERACTIVE": "Never",
            "GIT_ASKPASS": "",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_TERMINAL_PROMPT": "0",
        }
    )
    try:
        completed = subprocess.run(
            [
                "git",
                "-c",
                "credential.helper=",
                "ls-remote",
                "--symref",
                repository_url,
                "HEAD",
                f"refs/heads/{DEFAULT_BRANCH}",
            ],
            check=True,
            capture_output=True,
            text=True,
            env=environment,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise PublicSurfaceCheckError(
            "Anonymous git access failed for the canonical repository"
        ) from error
    return parse_remote_head(completed.stdout)


def parse_remote_head(output: str) -> tuple[str, str]:
    """Return the default branch and its commit from ``git ls-remote`` output."""

    branch: str | None = None
    head_commit: str | None = None
    branch_commit: str | None = None
    for line in output.splitlines():
        if line.startswith("ref: ") and line.endswith("\tHEAD"):
            reference = line.removeprefix("ref: ").removesuffix("\tHEAD")
            branch = reference.removeprefix("refs/heads/")
            continue
        fields = line.split("\t", maxsplit=1)
        if len(fields) != 2:
            continue
        commit, reference = fields
        if reference == "HEAD":
            head_commit = commit
        elif reference == f"refs/heads/{DEFAULT_BRANCH}":
            branch_commit = commit

    if branch is None or head_commit is None or branch_commit is None:
        raise PublicSurfaceCheckError(
            "Anonymous git response did not expose HEAD and the main branch"
        )
    if head_commit != branch_commit:
        raise PublicSurfaceCheckError(
            "Anonymous repository HEAD and main branch point to different commits"
        )
    return branch, head_commit


def _validate_bundle(bundle: Path, commit: str) -> str:
    if not bundle.is_file():
        raise PublicSurfaceCheckError(f"Review bundle does not exist: {bundle}")
    try:
        with zipfile.ZipFile(bundle) as archive:
            manifest = json.loads(archive.read("_meta/manifest.json"))
    except (
        KeyError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        zipfile.BadZipFile,
    ) as error:
        raise PublicSurfaceCheckError(
            "Review bundle has no valid embedded manifest"
        ) from error
    if not isinstance(manifest, dict):
        raise PublicSurfaceCheckError("Review-bundle manifest is not an object")
    if manifest.get("schema_version") != 3:
        raise PublicSurfaceCheckError("Review-bundle manifest schema is not version 3")

    copyright_data = manifest.get("copyright")
    expected_copyright = {
        "holder": EXPECTED_COPYRIGHT_HOLDER,
        "years": EXPECTED_COPYRIGHT_YEARS,
        "notice_path": "COPYRIGHT.md",
        "third_party_notice_path": "THIRD_PARTY.md",
    }
    if copyright_data != expected_copyright:
        raise PublicSurfaceCheckError(
            "Review-bundle copyright declaration does not match the public contract"
        )

    git = manifest.get("git")
    if not isinstance(git, dict):
        raise PublicSurfaceCheckError("Review-bundle Git metadata is missing")
    if git.get("commit") != commit:
        raise PublicSurfaceCheckError(
            "Review bundle does not describe the exposed commit"
        )
    if git.get("dirty") is not False or git.get("status") != []:
        raise PublicSurfaceCheckError(
            "Review bundle was not built from a clean candidate"
        )
    if manifest.get("missing_critical_paths") != []:
        raise PublicSurfaceCheckError(
            "Review bundle reports missing critical public paths"
        )
    return _sha256(bundle)


def _require_markers(name: str, payload: bytes, markers: tuple[str, ...]) -> None:
    source = payload.decode("utf-8", errors="replace")
    missing = tuple(marker for marker in markers if marker not in source)
    if missing:
        raise PublicSurfaceCheckError(
            f"Public {name} is missing expected markers: {', '.join(missing)}"
        )


def validate_public_surfaces(
    commit: str,
    bundle: Path,
    *,
    fetcher: Fetcher = _fetch,
    remote_reader: RemoteReader = _anonymous_remote_head,
    checked_at: datetime | None = None,
) -> dict[str, object]:
    """Validate anonymous GitHub access and return non-sensitive evidence."""

    if COMMIT_PATTERN.fullmatch(commit) is None:
        raise PublicSurfaceCheckError(
            "The exposed commit must be a full lowercase Git SHA"
        )

    bundle_digest = _validate_bundle(bundle, commit)
    branch, remote_commit = remote_reader(REPOSITORY_URL)
    if branch != DEFAULT_BRANCH:
        raise PublicSurfaceCheckError(
            f"Expected default branch {DEFAULT_BRANCH!r}, got {branch!r}"
        )
    if remote_commit != commit:
        raise PublicSurfaceCheckError(
            "The public main branch does not point to the accepted commit"
        )

    try:
        metadata = json.loads(fetcher(API_URL, "application/vnd.github+json"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PublicSurfaceCheckError(
            "GitHub repository metadata is not valid JSON"
        ) from error
    if not isinstance(metadata, dict):
        raise PublicSurfaceCheckError("GitHub repository metadata is invalid")
    license_data = metadata.get("license")
    license_id = license_data.get("spdx_id") if isinstance(license_data, dict) else None
    expected_metadata = {
        "private": False,
        "default_branch": DEFAULT_BRANCH,
        "has_issues": True,
        "archived": False,
    }
    for field, expected in expected_metadata.items():
        if metadata.get(field) != expected:
            raise PublicSurfaceCheckError(
                f"GitHub repository metadata {field!r} is not {expected!r}"
            )
    if license_id not in (*UNASSERTED_LICENSE_IDS, EXPECTED_LICENSE):
        raise PublicSurfaceCheckError(
            "GitHub identifies a repository license that conflicts with "
            f"{EXPECTED_LICENSE}"
        )

    checked_surfaces = ["anonymous git", "repository metadata"]
    raw_root = f"https://raw.githubusercontent.com/KintanaOne/Toetra/{commit}"
    for name, (path, markers) in RAW_SURFACES.items():
        _require_markers(
            name,
            fetcher(f"{raw_root}/{path}", "text/plain"),
            markers,
        )
        checked_surfaces.append(name)
    for name, (url, markers) in HTML_SURFACES.items():
        _require_markers(name, fetcher(url, "text/html"), markers)
        checked_surfaces.append(name)

    moment = checked_at or datetime.now(timezone.utc)
    return {
        "schema": "toetra.public-exposure-evidence",
        "schema_version": 1,
        "checked_at_utc": moment.astimezone(timezone.utc).isoformat(),
        "repository_url": REPOSITORY_URL,
        "default_branch": branch,
        "exposed_commit": commit,
        "review_bundle_sha256": bundle_digest,
        "github_detected_license": license_id,
        "copyright_holder": EXPECTED_COPYRIGHT_HOLDER,
        "copyright_years": EXPECTED_COPYRIGHT_YEARS,
        "anonymous_surfaces": checked_surfaces,
        "manual_settings_review": "required",
    }


def _local_commit(repository: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repository,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise PublicSurfaceCheckError("Cannot resolve the local Git commit") from error
    return completed.stdout.strip()


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repository",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    parser.add_argument("--commit")
    parser.add_argument(
        "--bundle",
        type=Path,
        default=Path("dist/toetra_review_bundle.zip"),
    )
    parser.add_argument(
        "--evidence-output",
        type=Path,
        default=Path("dist/p27-public-exposure-evidence.json"),
    )
    arguments = parser.parse_args(argv)
    commit = arguments.commit or _local_commit(arguments.repository)

    try:
        evidence = validate_public_surfaces(commit, arguments.bundle)
    except PublicSurfaceCheckError as error:
        print(f"Public surface check failed: {error}", file=sys.stderr)
        return 1

    arguments.evidence_output.parent.mkdir(parents=True, exist_ok=True)
    arguments.evidence_output.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("Toetra anonymous public surfaces: valid.")
    print(f"Exposed commit: {evidence['exposed_commit']}")
    print(f"Review bundle SHA-256: {evidence['review_bundle_sha256']}")
    print(f"Evidence written to: {arguments.evidence_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
