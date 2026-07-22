"""Safely add the FORML 1.0.0rc2 release entry to a changelog."""

from __future__ import annotations

import argparse
from pathlib import Path

RELEASE_MARKER = "[1.0.0rc2]"
RELEASE_SECTION = """## [1.0.0rc2] - 2026-07-22

### Added

- Public direct binary sklearn `LogisticRegression` verification route.
- Declarative label/probability observables, pairwise relations, reporting,
  replay, and clean-install classification smoke tests.

### Fixed

- Stable Decimal provenance canonicalization and certified logistic-threshold
  interval materialization.

### Compatibility

- JSON report schema v5 remains additive and the `LinearRegression` route is
  unchanged.

"""


def update_changelog(path: Path) -> bool:
    source = path.read_text(encoding="utf-8") if path.is_file() else "# Changelog\n\n"
    if RELEASE_MARKER in source:
        return False
    if source.startswith("# "):
        index = source.find("\n")
        prefix = source[: index + 1].rstrip() + "\n\n"
        remainder = source[index + 1 :].lstrip("\n")
        updated = prefix + RELEASE_SECTION + remainder
    else:
        updated = "# Changelog\n\n" + RELEASE_SECTION + source.lstrip()
    path.write_text(updated.rstrip() + "\n", encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", type=Path, default=Path("CHANGELOG.md"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        source = args.path.read_text(encoding="utf-8") if args.path.is_file() else ""
        if RELEASE_MARKER not in source:
            print(f"Missing {RELEASE_MARKER} in {args.path}")
            return 1
        print(f"Changelog contains {RELEASE_MARKER}.")
        return 0
    changed = update_changelog(args.path)
    print(f"{'Added' if changed else 'Found'} {RELEASE_MARKER} in {args.path}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
