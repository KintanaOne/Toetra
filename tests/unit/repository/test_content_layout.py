from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[3]


def test_repository_layout_is_documented() -> None:
    assert (ROOT / "docs" / "development" / "repository-layout.md").is_file()


def test_complete_examples_live_under_demo() -> None:
    cleveland = ROOT / "demo" / "classification" / "cleveland"

    assert not (ROOT / "examples").exists()
    assert (cleveland / "README.md").is_file()
    assert (cleveland / "train.py").is_file()
    assert (cleveland / "data" / "heart-disease-cleveland.csv").is_file()
    assert not (cleveland / "heart_clean.csv").exists()
    assert not (cleveland / "schema.json").exists()


def test_installed_examples_remain_small_package_resources() -> None:
    examples = ROOT / "src" / "toetra" / "examples"
    files = {
        path.relative_to(examples).as_posix()
        for path in examples.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }

    assert files == {"__init__.py", "credit_risk_policy.toetra"}


def test_completed_roadmaps_are_separate_from_active_plans() -> None:
    active = ROOT / "docs" / "roadmap"
    history = ROOT / "docs" / "history" / "roadmaps"
    completed = {
        "point-binding-evaluation-implementation-roadmap.md",
        "binary-classification-implementation-roadmap.md",
        "toetra-identity-migration-roadmap.md",
    }

    assert (history / "index.md").is_file()
    assert all((history / name).is_file() for name in completed)
    assert all(not (active / name).exists() for name in completed)
