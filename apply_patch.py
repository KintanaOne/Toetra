from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

PATCH_DIR = Path(__file__).resolve().parent
PAYLOAD_DIR = PATCH_DIR / "payload"
MANIFEST_PATH = PATCH_DIR / "manifest.json"


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def accepted_before_hashes(entry: dict) -> set[str]:
    hashes = set(entry.get("alternate_before_sha256", []))
    if entry.get("before_sha256") is not None:
        hashes.add(entry["before_sha256"])
    return hashes


def state_for(target: Path, entry: dict) -> str:
    destination = target / entry["path"]
    if not destination.exists():
        return "before" if entry.get("before_sha256") is None else "missing"
    if not destination.is_file():
        return "diverged"

    current = digest(destination)
    if current == entry["after_sha256"]:
        return "after"
    if current in accepted_before_hashes(entry):
        return "before"
    return "diverged"


def atomic_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", dir=destination.parent
    )
    os.close(file_descriptor)
    temporary = Path(temporary_name)
    try:
        shutil.copyfile(source, temporary)
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Apply FORML Patch 16.2 with baseline checksum checks."
    )
    parser.add_argument("target", nargs="?", default=".", help="FORML repository root")
    parser.add_argument(
        "--check", action="store_true", help="Check preconditions without writing"
    )
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    required_roots = (
        target / "pyproject.toml",
        target / "dsl",
        target / "model",
        target / "docs",
    )
    if not required_roots[0].is_file() or any(
        not path.is_dir() for path in required_roots[1:]
    ):
        print(
            f"ERROR: {target} does not look like a FORML repository root.",
            file=sys.stderr,
        )
        return 2

    manifest = load_manifest()
    states = {entry["path"]: state_for(target, entry) for entry in manifest["files"]}

    invalid = [
        path for path, state in states.items() if state in {"missing", "diverged"}
    ]
    if invalid:
        print("ERROR: Patch 16.2 preconditions failed for:", file=sys.stderr)
        for path in invalid:
            print(f"  - {path}: {states[path]}", file=sys.stderr)
        print(
            "No file was modified. Ensure Patch 16.1 revision 2 is applied and "
            "that the listed files have not diverged.",
            file=sys.stderr,
        )
        return 3

    if all(state == "after" for state in states.values()):
        print("FORML Patch 16.2 is already applied.")
        return 0

    pending = sum(state == "before" for state in states.values())
    print(f"Preconditions valid for FORML Patch 16.2 ({pending} file(s) pending).")
    if args.check:
        return 0

    for entry in manifest["files"]:
        if states[entry["path"]] == "after":
            continue
        source = PAYLOAD_DIR / entry["path"]
        destination = target / entry["path"]
        if not source.is_file() or digest(source) != entry["after_sha256"]:
            print(
                f"ERROR: payload checksum mismatch for {entry['path']}",
                file=sys.stderr,
            )
            return 5
        atomic_copy(source, destination)

    invalid_after = [
        entry["path"]
        for entry in manifest["files"]
        if state_for(target, entry) != "after"
    ]
    if invalid_after:
        print(
            f"ERROR: post-application verification failed: {invalid_after}",
            file=sys.stderr,
        )
        return 6

    print("FORML Patch 16.2 applied successfully.")
    print("Next: run `python -m mkdocs build --strict` and `make ci`.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
