"""Build and validate reproducible Python distribution artifacts."""

from __future__ import annotations

import gzip
import hashlib
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from dataclasses import dataclass
from email.parser import Parser
from pathlib import Path, PurePosixPath
from typing import BinaryIO, Iterable

from packaging.utils import parse_sdist_filename, parse_wheel_filename

DEFAULT_SOURCE_DATE_EPOCH = 1_700_000_000
EXPECTED_DISTRIBUTION_NAME = "toetra"
EXPECTED_TOP_LEVEL_PACKAGES = ("toetra", "dsl", "model")
FORBIDDEN_TOP_LEVEL_PACKAGES = ("forml",)
EXPECTED_PACKAGE_DATA = (
    "dsl/language/grammar/toetra_grammar.ebnf",
    "dsl/language/grammar/toetra_grammar.lark",
    "toetra/examples/credit_risk_policy.toetra",
)


class DistributionContractError(RuntimeError):
    """Raised when a distribution artifact violates the release contract."""


@dataclass(frozen=True, slots=True)
class DistributionArtifacts:
    """The wheel and source distribution produced by one build."""

    wheel: Path
    sdist: Path

    def sha256(self) -> dict[str, str]:
        return {
            self.wheel.name: sha256_file(self.wheel),
            self.sdist.name: sha256_file(self.sdist),
        }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_date_epoch(repository: Path) -> int:
    """Return the deterministic timestamp used for release artifacts."""

    raw = os.environ.get("SOURCE_DATE_EPOCH")
    if raw is not None:
        try:
            value = int(raw)
        except ValueError as exc:
            raise DistributionContractError(
                "SOURCE_DATE_EPOCH must be an integer number of seconds."
            ) from exc
        if value < 315_532_800:
            raise DistributionContractError(
                "SOURCE_DATE_EPOCH must be on or after 1980-01-01."
            )
        return value

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


def _safe_archive_path(name: str) -> PurePosixPath:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts:
        raise DistributionContractError(f"Unsafe archive path: {name!r}")
    return path


def normalize_sdist(path: Path, *, epoch: int) -> None:
    """Rewrite an sdist with deterministic order, ownership and timestamps."""

    with tarfile.open(path, mode="r:gz") as archive:
        entries: list[tuple[tarfile.TarInfo, bytes | None]] = []
        for member in archive.getmembers():
            _safe_archive_path(member.name)
            payload: bytes | None = None
            if member.isfile():
                extracted = archive.extractfile(member)
                if extracted is None:
                    raise DistributionContractError(
                        f"Unable to read sdist member {member.name!r}."
                    )
                payload = extracted.read()
            entries.append((member, payload))

    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as raw_stream:
        with gzip.GzipFile(
            filename="",
            mode="wb",
            fileobj=raw_stream,
            mtime=epoch,
        ) as gzip_stream:
            with tarfile.open(
                fileobj=gzip_stream,
                mode="w",
                format=tarfile.PAX_FORMAT,
            ) as output:
                for source, payload in sorted(entries, key=lambda item: item[0].name):
                    member = tarfile.TarInfo(source.name)
                    member.mode = source.mode
                    member.type = source.type
                    member.linkname = source.linkname
                    member.size = len(payload) if payload is not None else 0
                    member.mtime = epoch
                    member.uid = 0
                    member.gid = 0
                    member.uname = ""
                    member.gname = ""
                    member.pax_headers = {}
                    stream: BinaryIO | None = None
                    if payload is not None:
                        from io import BytesIO

                        stream = BytesIO(payload)
                    output.addfile(member, stream)
    temporary.replace(path)


def _staging_ignore(_directory: str, names: list[str]) -> set[str]:
    return {
        name
        for name in names
        if name
        in {
            ".git",
            ".hypothesis",
            ".pytest_cache",
            ".ruff_cache",
            ".venv",
            "__pycache__",
            "build",
            "dist",
            "site",
            "venv",
        }
        or name.endswith((".egg-info", ".pyc", ".pyo"))
    }


def _run_build(repository: Path, output: Path, *, epoch: int) -> None:
    output.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment["SOURCE_DATE_EPOCH"] = str(epoch)
    environment["PYTHONHASHSEED"] = "0"
    with tempfile.TemporaryDirectory(prefix="toetra-build-source-") as raw_directory:
        staged = Path(raw_directory) / "source"
        shutil.copytree(repository, staged, ignore=_staging_ignore)
        subprocess.run(
            [sys.executable, "-m", "build", "--outdir", str(output)],
            cwd=staged,
            env=environment,
            check=True,
        )


def _discover_artifacts(directory: Path) -> DistributionArtifacts:
    wheels = sorted(directory.glob("*.whl"))
    sdists = sorted(directory.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise DistributionContractError(
            "Expected exactly one wheel and one .tar.gz source distribution in "
            f"{directory}; found {len(wheels)} wheel(s) and {len(sdists)} sdist(s)."
        )
    return DistributionArtifacts(wheel=wheels[0], sdist=sdists[0])


def _write_checksums(artifacts: DistributionArtifacts) -> Path:
    checksum_path = artifacts.wheel.parent / "SHA256SUMS"
    lines = [f"{digest}  {name}" for name, digest in sorted(artifacts.sha256().items())]
    checksum_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return checksum_path


def ensure_clean_repository(repository: Path) -> None:
    """Require release artifacts to originate from one committed source state."""

    try:
        completed = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=repository,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise DistributionContractError(
            "A clean Git checkout is required for release artifacts."
        ) from exc

    status = completed.stdout.strip()
    if status:
        raise DistributionContractError(
            "Release artifacts require a clean Git checkout. Pending changes:\n"
            + status
        )


def build_distributions(
    repository: Path,
    output: Path,
    *,
    check_reproducible: bool = False,
    require_clean: bool = False,
) -> DistributionArtifacts:
    """Build release artifacts and optionally prove byte reproducibility."""

    repository = repository.resolve()
    output = output.resolve()
    if require_clean:
        ensure_clean_repository(repository)
    epoch = source_date_epoch(repository)

    if output.exists():
        shutil.rmtree(output)
    _run_build(repository, output, epoch=epoch)
    artifacts = _discover_artifacts(output)
    normalize_sdist(artifacts.sdist, epoch=epoch)
    check_distribution_directory(output)

    if not check_reproducible:
        _write_checksums(artifacts)
        return artifacts

    with tempfile.TemporaryDirectory(prefix="toetra-dist-repro-") as raw_directory:
        second_output = Path(raw_directory)
        _run_build(repository, second_output, epoch=epoch)
        second = _discover_artifacts(second_output)
        normalize_sdist(second.sdist, epoch=epoch)
        check_distribution_directory(second_output)

        first_hashes = artifacts.sha256()
        second_hashes = second.sha256()
        if first_hashes != second_hashes:
            raise DistributionContractError(
                "Distribution build is not byte-reproducible. "
                f"First={first_hashes}, second={second_hashes}"
            )

    _write_checksums(artifacts)
    return artifacts


def _metadata_from_wheel(archive: zipfile.ZipFile) -> dict[str, str]:
    metadata_names = [
        name for name in archive.namelist() if name.endswith(".dist-info/METADATA")
    ]
    if len(metadata_names) != 1:
        raise DistributionContractError(
            "Wheel must contain exactly one .dist-info/METADATA file."
        )
    content = archive.read(metadata_names[0]).decode("utf-8")
    parsed = Parser().parsestr(content)
    return {"name": parsed.get("Name", ""), "version": parsed.get("Version", "")}


def _check_required_members(members: Iterable[str], *, archive_kind: str) -> None:
    normalized = tuple(str(_safe_archive_path(name)) for name in members)
    for package in FORBIDDEN_TOP_LEVEL_PACKAGES:
        leaked = [name for name in normalized if package in PurePosixPath(name).parts]
        if leaked:
            raise DistributionContractError(
                f"{archive_kind} contains forbidden legacy package {package!r}: "
                f"{leaked[:5]}"
            )
    for package in EXPECTED_TOP_LEVEL_PACKAGES:
        marker = f"{package}/"
        if not any(
            marker in name or name.endswith(f"/{package}/__init__.py")
            for name in normalized
        ):
            raise DistributionContractError(
                f"{archive_kind} does not contain the {package!r} package."
            )
    for resource in EXPECTED_PACKAGE_DATA:
        if not any(
            name == resource or name.endswith(f"/{resource}") for name in normalized
        ):
            raise DistributionContractError(
                f"{archive_kind} does not contain required package data {resource!r}."
            )


def _check_wheel(path: Path) -> tuple[str, str]:
    name, version, _build, _tags = parse_wheel_filename(path.name)
    with zipfile.ZipFile(path) as archive:
        members = archive.namelist()
        _check_required_members(members, archive_kind="Wheel")
        forbidden = ("test/", "tests/", "docs/", "demo/", ".github/")
        leaked = [member for member in members if member.startswith(forbidden)]
        if leaked:
            raise DistributionContractError(
                f"Wheel contains repository-only paths: {leaked[:5]}"
            )
        metadata = _metadata_from_wheel(archive)
    if metadata["name"].lower().replace("-", "_") != name:
        raise DistributionContractError(
            "Wheel filename and METADATA project names differ."
        )
    if metadata["version"] != str(version):
        raise DistributionContractError("Wheel filename and METADATA versions differ.")
    return name, str(version)


def _check_sdist(path: Path) -> tuple[str, str]:
    name, version = parse_sdist_filename(path.name)
    with tarfile.open(path, mode="r:gz") as archive:
        members = [member.name for member in archive.getmembers()]
        _check_required_members(members, archive_kind="Source distribution")
        for required in ("pyproject.toml", "README.md", "CHANGELOG.md", "LICENSE"):
            if not any(member.endswith(f"/{required}") for member in members):
                raise DistributionContractError(
                    f"Source distribution does not contain {required!r}."
                )
    return name, str(version)


def check_distribution_directory(directory: Path) -> DistributionArtifacts:
    """Validate wheel/sdist inventory, metadata and package data."""

    artifacts = _discover_artifacts(directory)
    wheel_identity = _check_wheel(artifacts.wheel)
    sdist_identity = _check_sdist(artifacts.sdist)
    if wheel_identity != sdist_identity:
        raise DistributionContractError(
            "Wheel and source distribution identify different projects: "
            f"wheel={wheel_identity}, sdist={sdist_identity}."
        )
    if wheel_identity[0] != EXPECTED_DISTRIBUTION_NAME:
        raise DistributionContractError(
            "Distribution project name must be "
            f"{EXPECTED_DISTRIBUTION_NAME!r}, got {wheel_identity[0]!r}."
        )
    return artifacts
