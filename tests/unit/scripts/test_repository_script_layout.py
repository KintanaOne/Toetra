from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[3]
EXPECTED_ROOT_SCRIPTS = {
    "__init__.py",
    "build_distribution.py",
    "build_review_bundle.py",
    "check_distribution.py",
    "check_installed_distribution.py",
    "check_public_contract.py",
    "check_identity_contract.py",
    "clean_notebooks.py",
    "generate_numeric_compatibility_matrices.py",
}


def test_repository_scripts_contain_only_permanent_automation() -> None:
    scripts = ROOT / "scripts"
    root_scripts = {path.name for path in scripts.glob("*.py")}
    historical_migrations = tuple((scripts / "migrations").glob("*.py"))

    assert root_scripts == EXPECTED_ROOT_SCRIPTS
    assert not historical_migrations
    assert not (scripts / "prepare_rc2_changelog.py").exists()
