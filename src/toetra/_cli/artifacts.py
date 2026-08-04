"""Atomic verification artifact sets and their completion manifest."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable, Mapping

from toetra._cli.output import write_atomic_text
from toetra._runtime.errors import (
    VerificationConfigurationError,
    VerificationRuntimeError,
)

if TYPE_CHECKING:
    from toetra._runtime.session import VerificationSession


RUN_MANIFEST_SCHEMA = "toetra.run-manifest"
RUN_MANIFEST_SCHEMA_VERSION = 1
VERIFICATION_COLLECTION_SCHEMA = "toetra.verification-report-collection"
VERIFICATION_COLLECTION_SCHEMA_VERSION = 6


@dataclass(frozen=True)
class VerificationCollectionSummary:
    """Validated identity of one rendered verification collection."""

    schema: str
    schema_version: int
    report_count: int


@dataclass(frozen=True)
class VerificationArtifactSet:
    """Resolved paths and rendered content for one verification artifact set."""

    directory: Path
    stem: str
    json_path: Path
    html_path: Path
    manifest_path: Path
    json_text: str
    html_text: str
    verification: VerificationCollectionSummary

    @property
    def paths(self) -> tuple[Path, Path, Path]:
        return self.json_path, self.html_path, self.manifest_path


def verification_artifact_paths(
    directory: str | Path,
    stem: str,
) -> tuple[Path, Path, Path]:
    """Resolve the three stable output paths for one artifact stem."""

    root = Path(directory).expanduser().resolve()
    return (
        root / f"{stem}.json",
        root / f"{stem}.html",
        root / f"{stem}.manifest.json",
    )


def build_verification_artifact_set(
    *,
    directory: str | Path,
    stem: str,
    json_text: str,
    html_text: str,
    verification: VerificationCollectionSummary,
) -> VerificationArtifactSet:
    """Resolve artifact paths for reports rendered from one session."""

    root = Path(directory).expanduser().resolve()
    json_path, html_path, manifest_path = verification_artifact_paths(root, stem)
    return VerificationArtifactSet(
        directory=root,
        stem=stem,
        json_path=json_path,
        html_path=html_path,
        manifest_path=manifest_path,
        json_text=json_text,
        html_text=html_text,
        verification=verification,
    )


def validate_verification_collection_json(
    text: str,
    *,
    expected_report_count: int,
) -> VerificationCollectionSummary:
    """Validate the exact JSON v6 collection rendered by a session."""

    try:
        payload = json.loads(text)
    except (TypeError, json.JSONDecodeError) as error:
        raise VerificationRuntimeError(
            "Verification JSON rendering did not produce valid JSON.",
            code="CLI_VERIFICATION_JSON_INVALID",
            stage="output",
            hint="Report this failure with the associated verification inputs.",
        ) from error
    if not isinstance(payload, dict):
        raise VerificationRuntimeError(
            "Verification JSON rendering did not produce a collection object.",
            code="CLI_VERIFICATION_JSON_INVALID",
            stage="output",
            hint="Report this failure with the associated verification inputs.",
        )

    schema = payload.get("schema")
    schema_version = payload.get("schema_version")
    report_count = payload.get("report_count")
    reports = payload.get("reports")
    if (
        schema != VERIFICATION_COLLECTION_SCHEMA
        or schema_version != VERIFICATION_COLLECTION_SCHEMA_VERSION
        or isinstance(report_count, bool)
        or not isinstance(report_count, int)
        or report_count != expected_report_count
        or not isinstance(reports, list)
        or len(reports) != report_count
    ):
        raise VerificationRuntimeError(
            "Verification JSON rendering violated the frozen collection contract.",
            code="CLI_VERIFICATION_JSON_CONTRACT_MISMATCH",
            stage="output",
            hint="Report this failure with the associated verification inputs.",
        )
    return VerificationCollectionSummary(
        schema=schema,
        schema_version=schema_version,
        report_count=report_count,
    )


def write_verification_report_artifacts(
    artifact_set: VerificationArtifactSet,
    *,
    consumed_paths: Iterable[Path],
    reserved_paths: Iterable[Path] = (),
) -> Mapping[str, Path]:
    """Write report artifacts atomically, intentionally excluding the manifest."""

    all_reserved = {Path(path).expanduser().resolve() for path in reserved_paths}
    all_reserved.add(artifact_set.manifest_path.resolve())
    _invalidate_previous_manifest(artifact_set.manifest_path)
    json_path = write_atomic_text(
        artifact_set.json_text,
        artifact_set.json_path,
        consumed_paths=consumed_paths,
        reserved_paths={*all_reserved, artifact_set.html_path.resolve()},
    )
    html_path = write_atomic_text(
        artifact_set.html_text,
        artifact_set.html_path,
        consumed_paths=consumed_paths,
        reserved_paths={*all_reserved, artifact_set.json_path.resolve()},
    )
    return {"json": json_path, "html": html_path}


def _invalidate_previous_manifest(path: Path) -> None:
    """Remove a stale completion marker before replacing report artifacts."""

    try:
        path.lstat()
    except (FileNotFoundError, NotADirectoryError):
        return
    except OSError as error:
        raise VerificationRuntimeError(
            f"Failed to inspect the previous CLI run manifest: {path}",
            code="CLI_MANIFEST_INVALIDATION_FAILED",
            stage="output",
            hint="Check manifest permissions before retrying the verification run.",
            path=str(path),
        ) from error

    try:
        path.unlink()
    except OSError as error:
        raise VerificationRuntimeError(
            f"Failed to invalidate the previous CLI run manifest: {path}",
            code="CLI_MANIFEST_INVALIDATION_FAILED",
            stage="output",
            hint="Check manifest permissions before retrying the verification run.",
            path=str(path),
        ) from error


def build_run_manifest(
    session: VerificationSession,
    *,
    artifacts: VerificationArtifactSet,
    process_status: int,
    primary_format: str,
    primary_destination: str,
    started_at_utc: str,
    completed_at_utc: str,
    duration_ms: float,
) -> dict[str, Any]:
    """Build the stable completion manifest for one verification command."""

    provenance = session.provenance
    software = provenance.software if provenance is not None else None
    return {
        "schema": RUN_MANIFEST_SCHEMA,
        "schema_version": RUN_MANIFEST_SCHEMA_VERSION,
        "command": "verify",
        "process_status": process_status,
        "started_at_utc": started_at_utc,
        "completed_at_utc": completed_at_utc,
        "duration_ms": round(max(duration_ms, 0.0), 3),
        "primary_output": {
            "format": primary_format,
            "destination": "stdout" if primary_destination == "-" else "file",
            "path": None if primary_destination == "-" else primary_destination,
        },
        "verification": {
            "schema": artifacts.verification.schema,
            "schema_version": artifacts.verification.schema_version,
            "report_count": artifacts.verification.report_count,
            "input_fingerprint": (
                provenance.input_fingerprint if provenance is not None else None
            ),
            "provenance_completeness": (
                provenance.completeness.value if provenance is not None else None
            ),
        },
        "artifacts": {
            "json": _artifact_record(artifacts.json_path, artifacts.directory),
            "html": _artifact_record(artifacts.html_path, artifacts.directory),
        },
        "software": {
            "toetra_version": (
                software.toetra_version if software is not None else _version()
            ),
            "toetra_build_id": (
                software.toetra_build_id if software is not None else None
            ),
        },
    }


def write_run_manifest(
    manifest: Mapping[str, Any],
    *,
    artifact_set: VerificationArtifactSet,
    consumed_paths: Iterable[Path],
    reserved_paths: Iterable[Path] = (),
) -> Path:
    """Commit the completion manifest after every other output succeeded."""

    manifest_reserved = {Path(path).expanduser().resolve() for path in reserved_paths}
    manifest_reserved.update(
        {artifact_set.json_path.resolve(), artifact_set.html_path.resolve()}
    )
    try:
        rendered = json.dumps(manifest, ensure_ascii=False, indent=2)
    except (TypeError, ValueError) as error:
        raise VerificationRuntimeError(
            "Failed to render the CLI run manifest.",
            code="CLI_MANIFEST_RENDER_FAILED",
            stage="output",
            hint="Report this failure with the associated verification inputs.",
        ) from error
    return write_atomic_text(
        rendered,
        artifact_set.manifest_path,
        consumed_paths=consumed_paths,
        reserved_paths=manifest_reserved,
    )


def utc_now() -> str:
    """Return a canonical UTC timestamp for process-level manifests."""

    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def validate_artifact_stem(value: str) -> str:
    """Accept one portable filename stem rather than an arbitrary path."""

    if not value or value in {".", ".."} or len(value) > 128:
        raise VerificationConfigurationError(
            "Artifact stem must be a non-empty portable filename stem.",
            code="CLI_ARTIFACT_STEM_INVALID",
            stage="configuration",
            hint="Use 1-128 letters, digits, dots, underscores, or hyphens.",
        )
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")
    reserved_windows_names = {"CON", "PRN", "AUX", "NUL"}
    reserved_windows_names.update(f"COM{index}" for index in range(1, 10))
    reserved_windows_names.update(f"LPT{index}" for index in range(1, 10))
    base_name = value.split(".", maxsplit=1)[0].upper()
    if (
        value[0] in {".", "-"}
        or value.endswith(".")
        or base_name in reserved_windows_names
        or any(character not in allowed for character in value)
    ):
        raise VerificationConfigurationError(
            f"Invalid artifact stem: {value!r}",
            code="CLI_ARTIFACT_STEM_INVALID",
            stage="configuration",
            hint=(
                "Use a stem beginning with a letter, digit, or underscore and "
                "containing only letters, digits, dots, underscores, or hyphens."
            ),
        )
    return value


def _artifact_record(path: Path, directory: Path) -> dict[str, Any]:
    try:
        content = path.read_bytes()
    except OSError as error:
        raise VerificationRuntimeError(
            f"Failed to read completed CLI artifact: {path}",
            code="CLI_ARTIFACT_READ_FAILED",
            stage="output",
            hint="Check artifact permissions and storage integrity.",
            path=str(path),
        ) from error
    return {
        "path": path.relative_to(directory).as_posix(),
        "sha256": hashlib.sha256(content).hexdigest(),
        "size_bytes": len(content),
    }


def _version() -> str:
    try:
        return version("toetra")
    except PackageNotFoundError:
        return "unknown"
