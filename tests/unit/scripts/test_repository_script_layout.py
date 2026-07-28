from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[3]
EXPECTED_LAYOUT = {
    "ci": {"__init__.py", "check_public_contract.py", "clean_notebooks.py"},
    "docs": {
        "__init__.py",
        "check_snippets.py",
        "generate_numeric_compatibility_matrices.py",
    },
    "release": {
        "__init__.py",
        "build_distribution.py",
        "build_review_bundle.py",
        "check_distribution.py",
        "check_installed_distribution.py",
        "distribution.py",
        "review_bundle.py",
    },
    "repository": {
        "__init__.py",
        "check_identity_contract.py",
        "check_repository_contract.py",
    },
}


def test_repository_scripts_are_grouped_by_responsibility() -> None:
    scripts = ROOT / "scripts"
    root_scripts = {path.name for path in scripts.glob("*.py")}
    directories = {
        path.name
        for path in scripts.iterdir()
        if path.is_dir() and path.name != "__pycache__"
    }

    assert root_scripts == {"__init__.py"}
    assert directories == set(EXPECTED_LAYOUT)
    for directory, expected_files in EXPECTED_LAYOUT.items():
        actual_files = {path.name for path in (scripts / directory).glob("*.py")}
        assert actual_files == expected_files


def test_repository_contains_no_historical_migration_scripts() -> None:
    scripts = ROOT / "scripts"

    assert not (scripts / "migrations").exists()
    assert not (scripts / "prepare_rc2_changelog.py").exists()
