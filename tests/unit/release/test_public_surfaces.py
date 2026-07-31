from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

from scripts.release.check_public_surfaces import (
    API_URL,
    DEFAULT_BRANCH,
    DOCUMENTATION_URL,
    HTML_SURFACES,
    RAW_SURFACES,
    REPOSITORY_URL,
    PublicSurfaceCheckError,
    parse_remote_head,
    validate_public_surfaces,
)

COMMIT = "a" * 40


def _bundle(
    path: Path,
    *,
    commit: str = COMMIT,
    dirty: bool = False,
    copyright_holder: str = "Tina RANDRIANARIJAONA-DUBIN",
) -> Path:
    manifest = {
        "schema_version": 3,
        "git": {"commit": commit, "dirty": dirty, "status": []},
        "missing_critical_paths": [],
        "copyright": {
            "holder": copyright_holder,
            "years": "2025-2026",
            "notice_path": "COPYRIGHT.md",
            "third_party_notice_path": "THIRD_PARTY.md",
        },
    }
    with zipfile.ZipFile(path, mode="w") as archive:
        archive.writestr("_meta/manifest.json", json.dumps(manifest))
    return path


def _fetcher(url: str, accept: str) -> bytes:
    del accept
    if url == API_URL:
        return json.dumps(
            {
                "private": False,
                "default_branch": DEFAULT_BRANCH,
                "has_issues": True,
                "archived": False,
                "license": {"spdx_id": "PolyForm-Noncommercial-1.0.0"},
            }
        ).encode()
    if url == DOCUMENTATION_URL:
        return b"<title>Toetra</title>"
    for _, (surface_url, markers) in HTML_SURFACES.items():
        if url == surface_url:
            return " ".join(markers).encode()
    for _, (path, markers) in RAW_SURFACES.items():
        if url.endswith(f"/{path}"):
            return "\n".join(markers).encode()
    raise AssertionError(f"Unexpected URL: {url}")


def _fetcher_with_license(license_id: str | None):
    def fetch(url: str, accept: str) -> bytes:
        if url == API_URL:
            return json.dumps(
                {
                    "private": False,
                    "default_branch": DEFAULT_BRANCH,
                    "has_issues": True,
                    "archived": False,
                    "license": (
                        {"spdx_id": license_id} if license_id is not None else None
                    ),
                }
            ).encode()
        return _fetcher(url, accept)

    return fetch


def test_parse_remote_head_requires_one_default_branch_commit() -> None:
    output = "\n".join(
        (
            "ref: refs/heads/main\tHEAD",
            f"{COMMIT}\tHEAD",
            f"{COMMIT}\trefs/heads/main",
        )
    )

    assert parse_remote_head(output) == ("main", COMMIT)

    with pytest.raises(PublicSurfaceCheckError, match="did not expose"):
        parse_remote_head(f"{COMMIT}\tHEAD\n")


def test_public_surface_evidence_binds_remote_and_bundle_commit(
    tmp_path: Path,
) -> None:
    bundle = _bundle(tmp_path / "review.zip")
    checked_at = datetime(2026, 7, 31, 0, 0, tzinfo=timezone.utc)

    evidence = validate_public_surfaces(
        COMMIT,
        bundle,
        fetcher=_fetcher,
        remote_reader=lambda url: (
            (DEFAULT_BRANCH, COMMIT)
            if url == REPOSITORY_URL
            else pytest.fail("unexpected repository URL")
        ),
        checked_at=checked_at,
    )

    assert evidence["exposed_commit"] == COMMIT
    assert evidence["default_branch"] == "main"
    assert evidence["github_detected_license"] == "PolyForm-Noncommercial-1.0.0"
    assert evidence["copyright_holder"] == "Tina RANDRIANARIJAONA-DUBIN"
    assert evidence["copyright_years"] == "2025-2026"
    assert evidence["checked_at_utc"] == "2026-07-31T00:00:00+00:00"
    assert evidence["manual_settings_review"] == "required"
    assert evidence["review_bundle_sha256"]


def test_public_surface_check_rejects_wrong_remote_or_dirty_bundle(
    tmp_path: Path,
) -> None:
    bundle = _bundle(tmp_path / "review.zip")

    with pytest.raises(PublicSurfaceCheckError, match="does not point"):
        validate_public_surfaces(
            COMMIT,
            bundle,
            fetcher=_fetcher,
            remote_reader=lambda url: (DEFAULT_BRANCH, "b" * 40),
        )

    dirty_bundle = _bundle(tmp_path / "dirty.zip", dirty=True)
    with pytest.raises(PublicSurfaceCheckError, match="clean candidate"):
        validate_public_surfaces(
            COMMIT,
            dirty_bundle,
            fetcher=_fetcher,
            remote_reader=lambda url: (DEFAULT_BRANCH, COMMIT),
        )


def test_public_surface_check_rejects_wrong_copyright_holder(tmp_path: Path) -> None:
    bundle = _bundle(tmp_path / "review.zip", copyright_holder="Unexpected Holder")

    with pytest.raises(PublicSurfaceCheckError, match="copyright declaration"):
        validate_public_surfaces(
            COMMIT,
            bundle,
            fetcher=_fetcher,
            remote_reader=lambda _: (DEFAULT_BRANCH, COMMIT),
        )


@pytest.mark.parametrize("license_id", [None, "NOASSERTION"])
def test_public_surface_check_accepts_unasserted_github_license(
    tmp_path: Path,
    license_id: str | None,
) -> None:
    evidence = validate_public_surfaces(
        COMMIT,
        _bundle(tmp_path / "review.zip"),
        fetcher=_fetcher_with_license(license_id),
        remote_reader=lambda _: (DEFAULT_BRANCH, COMMIT),
    )

    assert evidence["github_detected_license"] == license_id


def test_public_surface_check_rejects_conflicting_github_license(
    tmp_path: Path,
) -> None:
    with pytest.raises(PublicSurfaceCheckError, match="conflicts"):
        validate_public_surfaces(
            COMMIT,
            _bundle(tmp_path / "review.zip"),
            fetcher=_fetcher_with_license("Apache-2.0"),
            remote_reader=lambda _: (DEFAULT_BRANCH, COMMIT),
        )
