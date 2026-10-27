"""Validate the exact stable archives before handing them to PyPI.

This uses only the standard library and never rebuilds, imports, or installs
the package. The caller has already run the complete reusable CI workflow.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import tarfile
import tomllib
import zipfile
from email.parser import Parser
from pathlib import Path


def validate_pypi_artifacts(
    directory: Path, *, version: str, project_file: Path
) -> None:
    if not re.fullmatch(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", version):
        raise ValueError("Enter an exact stable version, such as 1.0.0.")
    project = tomllib.loads(project_file.read_text(encoding="utf-8"))["project"]
    if project["name"] != "toetra" or project["version"] != version:
        raise ValueError(
            "Requested version does not match the verified Toetra sources."
        )

    names = {f"toetra-{version}-py3-none-any.whl", f"toetra-{version}.tar.gz"}
    if {path.name for path in directory.iterdir()} != names | {"SHA256SUMS"}:
        raise ValueError("Expected exactly the wheel, sdist, and SHA256SUMS.")
    checksums: dict[str, str] = {}
    for line in (directory / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([a-f0-9]{64})  (.+)", line)
        if match is None or match[2] not in names or match[2] in checksums:
            raise ValueError("Invalid or duplicate SHA256SUMS entry.")
        checksums[match[2]] = match[1]
    if checksums.keys() != names:
        raise ValueError("Checksums must cover both distribution archives exactly.")
    for name, expected in sorted(checksums.items()):
        archive = directory / name
        if not archive.is_file() or archive.is_symlink():
            raise ValueError("Distribution archives must be regular files.")
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        if digest != expected:
            raise ValueError(f"SHA256 mismatch for {name}.")
        if name.endswith(".whl"):
            with zipfile.ZipFile(archive) as wheel:
                raw = wheel.read(f"toetra-{version}.dist-info/METADATA")
        else:
            with tarfile.open(archive, "r:gz") as sdist:
                stream = sdist.extractfile(f"toetra-{version}/PKG-INFO")
                if stream is None:
                    raise ValueError("Source distribution metadata is missing.")
                with stream:
                    raw = stream.read()
        metadata = Parser().parsestr(raw.decode("utf-8"))
        if metadata["Name"] != "toetra" or metadata["Version"] != version:
            raise ValueError(f"Unexpected project or version in {name}.")
        print(f"Verified: {digest}  {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    validate_pypi_artifacts(
        arguments.directory,
        version=os.environ.get("RELEASE_VERSION", ""),
        project_file=Path(__file__).resolve().parents[2] / "pyproject.toml",
    )
    # Publish only archives, keeping SHA256SUMS out of the upload directory.
    arguments.output.mkdir(parents=True, exist_ok=False)
    for archive in sorted(arguments.directory.iterdir()):
        if archive.name != "SHA256SUMS":
            shutil.copyfile(archive, arguments.output / archive.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
