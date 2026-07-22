from __future__ import annotations

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).parents[3]


def test_make_ci_is_non_mutating() -> None:
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    ci_block = re.search(
        r"^ci:.*?(?=\n\S|\Z)", makefile, flags=re.MULTILINE | re.DOTALL
    )

    assert ci_block is not None
    text = ci_block.group(0)
    assert "black ." not in text
    assert "notebooks-clean" not in text
    assert "black --check" in makefile


def test_ci_covers_supported_python_versions_and_checks_checkout() -> None:
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert 'python-version: ["3.11", "3.12"]' in workflow
    assert "git status --porcelain" in workflow
    assert "make release-check" in workflow
    assert "make review-bundle-check" in workflow


def test_ci_installs_project_runtime_and_all_required_extras() -> None:
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    requirements = (ROOT / "requirements-dev.txt").read_text(encoding="utf-8")
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert workflow.count('python -m pip install ".[dev,docs]"') == 2
    assert "python -m pip install -r requirements-dev.txt" not in workflow
    assert "-e .[dev,docs]" in requirements
    assert 'python -m pip install -e ".[dev,docs]"' in makefile


def test_build_toolchain_and_dev_extra_are_pinned() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert project["build-system"]["requires"] == [
        "setuptools==82.0.1",
        "wheel==0.47.0",
    ]
    dev = project["project"]["optional-dependencies"]["dev"]
    assert "build==1.5.0" in dev
    assert all("==" in requirement for requirement in dev)


def test_rc2_release_probe_exercises_binary_classification() -> None:
    probe = (ROOT / "scripts" / "check_installed_distribution.py").read_text(
        encoding="utf-8"
    )
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "LogisticRegression" in probe
    assert "target[applicant].label" in probe
    assert "target[applicant].probability" in probe
    assert "VerificationStatus.WITNESS" in probe
    assert "release-metadata" in makefile
    assert "demo-classification" in makefile
