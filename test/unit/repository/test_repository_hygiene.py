from __future__ import annotations

import hashlib
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parents[3]
OBSOLETE_ROOT_FILES = {
    "apply_patch.py",
    "changes.diff",
    "context_helper.py",
    "manifest.json",
    "pipeline.txt",
}
OBSOLETE_DOCUMENTS = {
    "docs/docs-roadmap.md",
    "docs/review-corrections.md",
}
OBSOLETE_CODE_PATHS = {
    "dsl/builder/core/to_delete.py",
    "test/unit/parsing",
    "test/e2e/normalization/test_run_nnf.py",
    "test/hypothesis/mutation/functions/semantic/relationnal.py",
    "test/hypothesis/mutation/functions/structural/cooruotion.py",
}


def test_repository_has_no_historical_artifacts() -> None:
    present = {path.name for path in ROOT.iterdir() if path.name in OBSOLETE_ROOT_FILES}
    obsolete_code = {
        relative for relative in OBSOLETE_CODE_PATHS if (ROOT / relative).exists()
    }

    assert not present
    assert not obsolete_code
    assert not (ROOT / ".docs").exists()
    assert not tuple(ROOT.glob("toetra_review_bundle_*.zip"))
    assert not tuple(ROOT.glob("forml_review_bundle_*.zip"))
    assert not tuple(ROOT.glob("P*_*.patch"))


def test_completed_documentation_working_notes_are_absent() -> None:
    present = {
        relative for relative in OBSOLETE_DOCUMENTS if (ROOT / relative).exists()
    }

    assert not present


def test_local_review_artifacts_are_ignored() -> None:
    ignore_rules = {
        line.strip()
        for line in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }

    assert "/.docs/" in ignore_rules
    assert "/toetra_review_bundle_*.zip" in ignore_rules
    assert "/forml_review_bundle_*.zip" not in ignore_rules


def test_every_documentation_page_is_in_mkdocs_navigation() -> None:
    navigation = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    missing = {
        page.relative_to(ROOT / "docs").as_posix()
        for page in (ROOT / "docs").rglob("*.md")
        if page.relative_to(ROOT / "docs").as_posix() not in navigation
    }

    assert not missing


def test_repository_has_no_duplicate_test_modules() -> None:
    test_roots = tuple(
        path for name in ("test", "tests") if (path := ROOT / name).is_dir()
    )
    assert len(test_roots) == 1

    paths_by_digest: dict[str, list[str]] = defaultdict(list)
    for test_root in test_roots:
        for path in test_root.rglob("test_*.py"):
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            paths_by_digest[digest].append(path.relative_to(ROOT).as_posix())

    duplicates = tuple(
        sorted(paths) for paths in paths_by_digest.values() if len(paths) > 1
    )
    assert not duplicates


def test_repository_has_no_empty_python_modules() -> None:
    root_names = (
        "src",
        "toetra",
        "dsl",
        "model",
        "scripts",
        "demo",
        "test",
        "tests",
    )
    roots = tuple(ROOT / name for name in root_names if (ROOT / name).is_dir())
    empty_modules = {
        path.relative_to(ROOT).as_posix()
        for source_root in roots
        for path in source_root.rglob("*.py")
        if path.name != "__init__.py" and path.stat().st_size == 0
    }

    assert not empty_modules
