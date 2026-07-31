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


def _bundle(path: Path, *, commit: str = COMMIT, dirty: bool = False) -> Path:
    manifest = {
        "git": {"commit": commit, "dirty": dirty, "status": []},
        "missing_critical_paths": [],
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
                "license": {"spdx_id": "Apache-2.0"},
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
