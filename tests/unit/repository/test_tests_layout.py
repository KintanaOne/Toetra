from __future__ import annotations

import hashlib
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parents[3]
TESTS_ROOT = ROOT / "tests"
FIXTURES_ROOT = TESTS_ROOT / "fixtures"
GOLDEN_ROOT = TESTS_ROOT / "golden"
SUPPORT_ROOT = TESTS_ROOT / "support"


def test_test_tree_uses_the_canonical_top_level_layout() -> None:
    expected = {
        "e2e",
        "fixtures",
        "golden",
        "integration",
        "property_based",
        "support",
        "unit",
    }
    present = {
        path.name
        for path in TESTS_ROOT.iterdir()
        if path.is_dir() and path.name != "__pycache__"
    }

    assert TESTS_ROOT.is_dir()
    assert not (ROOT / "test").exists()
    assert present == expected
    assert not (TESTS_ROOT / "unit" / "ir2").exists()


def test_fixture_and_golden_assets_have_distinct_roles() -> None:
    ambiguous_fixture_directories = {
        path.relative_to(TESTS_ROOT).as_posix()
        for name in ("golden", "expected")
        for path in FIXTURES_ROOT.rglob(name)
        if path.is_dir()
    }
    ambiguous_golden_directories = {
        path.relative_to(TESTS_ROOT).as_posix()
        for name in ("cases", "fixtures")
        for path in GOLDEN_ROOT.rglob(name)
        if path.is_dir()
    }
    executable_goldens = {
        path.relative_to(TESTS_ROOT).as_posix() for path in GOLDEN_ROOT.rglob("*.py")
    }

    assert not ambiguous_fixture_directories
    assert not ambiguous_golden_directories
    assert not executable_goldens


def test_shared_test_helpers_live_under_support() -> None:
    obsolete_helpers = {
        "e2e/point_binding/_helpers.py",
        "unit/backends/z3_backend/_point_aware_helpers.py",
        "unit/builder/_point_binding_helpers.py",
        "unit/ir/ir2/_point_aware_helpers.py",
        "unit/parser/_point_binding_helpers.py",
        "unit/parser/_program_helpers.py",
        "unit/semantic/_point_binding_helpers.py",
        "unit/semantic/anchor_helpers.py",
        "unit/semantic/restriction_helpers.py",
    }
    present = {
        relative for relative in obsolete_helpers if (TESTS_ROOT / relative).exists()
    }

    assert SUPPORT_ROOT.is_dir()
    assert (SUPPORT_ROOT / "paths.py").is_file()
    assert not present


def test_fixture_inputs_are_not_duplicated() -> None:
    paths_by_digest: dict[str, list[str]] = defaultdict(list)
    for path in FIXTURES_ROOT.rglob("*"):
        if not path.is_file() or path.stat().st_size == 0:
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        paths_by_digest[digest].append(path.relative_to(TESTS_ROOT).as_posix())

    duplicates = tuple(
        sorted(paths) for paths in paths_by_digest.values() if len(paths) > 1
    )

    assert not duplicates
