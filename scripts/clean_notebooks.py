"""Strip transient execution state from Jupyter notebooks.

The project intentionally avoids a runtime dependency on ``nbformat``.  Notebook
files are JSON documents, so the small hygiene operation required by the local CI
can be implemented with the standard library.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterable
from pathlib import Path

DEFAULT_NOTEBOOK_ROOT = Path("demo/notebooks")


def iter_notebook_paths(paths: Iterable[Path]) -> tuple[Path, ...]:
    """Return all notebook files contained in *paths* in deterministic order."""

    notebooks: set[Path] = set()
    for path in paths:
        if path.is_dir():
            notebooks.update(path.rglob("*.ipynb"))
        elif path.suffix == ".ipynb" and path.is_file():
            notebooks.add(path)
    return tuple(sorted(notebooks))


def clean_notebook(path: Path, *, check: bool = False) -> bool:
    """Remove outputs and execution counters from one notebook.

    Returns ``True`` when transient state was found.  In check mode the file is
    left untouched; otherwise it is rewritten using the repository's canonical
    one-space JSON indentation.
    """

    notebook = json.loads(path.read_text(encoding="utf-8"))
    changed = False

    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue

        if cell.get("execution_count") is not None:
            cell["execution_count"] = None
            changed = True

        if cell.get("outputs"):
            cell["outputs"] = []
            changed = True

    metadata = notebook.get("metadata")
    if isinstance(metadata, dict) and "widgets" in metadata:
        metadata.pop("widgets")
        changed = True

    if changed and not check:
        path.write_text(
            json.dumps(notebook, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8",
        )

    return changed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Remove transient outputs from Jupyter notebooks.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        default=[DEFAULT_NOTEBOOK_ROOT],
        help="Notebook files or directories to scan.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report dirty notebooks without modifying them.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    notebooks = iter_notebook_paths(args.paths)
    dirty = [path for path in notebooks if clean_notebook(path, check=args.check)]

    if not dirty:
        print(f"Notebook hygiene: {len(notebooks)} clean notebook(s).")
        return 0

    if args.check:
        print("Notebook hygiene failed; transient outputs found in:")
        for path in dirty:
            print(f"  - {path}")
        return 1

    print(f"Notebook hygiene: cleaned {len(dirty)} notebook(s).")
    for path in dirty:
        print(f"  - {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
