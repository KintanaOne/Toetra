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
    format_check = re.search(
        r"^format-check:.*?(?=\n\S|\Z)",
        makefile,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert format_check is not None
    assert "black ." not in text
    assert "notebooks-clean" not in text
    assert "python -m black ." not in format_check.group(0)
    assert "python -m black --check ." in format_check.group(0)


def test_ci_covers_supported_python_versions_and_checks_checkout() -> None:
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert 'python-version: ["3.11", "3.12"]' in workflow
    assert "git status --porcelain" in workflow
    assert "make release-check" in workflow
    assert "make demo-check" in workflow
    assert "make review-bundle-check" in workflow
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "dist/toetra_review_bundle.zip" in makefile


def test_ci_installs_project_runtime_and_all_required_extras() -> None:
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    requirements = (ROOT / "requirements-dev.txt").read_text(encoding="utf-8")
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert workflow.count('python -m pip install ".[dev,docs]"') == 2
    assert "python -m pip install -r requirements-dev.txt" not in workflow
    assert "-e .[dev,docs]" in requirements
    assert 'python -m pip install -e ".[dev,docs]"' in makefile


def test_cli_entry_point_targets_the_private_process_adapter() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert project["project"]["scripts"] == {"toetra": "toetra._cli.main:main"}
    assert (ROOT / "src" / "toetra" / "__main__.py").is_file()


def test_build_toolchain_and_dev_extra_are_pinned() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert project["build-system"]["requires"] == [
        "setuptools==82.0.1",
        "wheel==0.47.0",
    ]
    dev = project["project"]["optional-dependencies"]["dev"]
    assert "build==1.5.0" in dev
    assert all("==" in requirement for requirement in dev)


def test_release_probe_exercises_binary_classification() -> None:
    probe = (
        ROOT / "scripts" / "release" / "check_installed_distribution.py"
    ).read_text(encoding="utf-8")
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "LogisticRegression" in probe
    assert "target[applicant].label" in probe
    assert "target[applicant].probability" in probe
    assert "VerificationStatus.WITNESS" in probe
    assert '"validate",' in probe
    assert '"inspect",' in probe
    assert '"replay",' in probe
    assert '"toetra.validation-result"' in probe
    assert '"toetra.inspection"' in probe
    assert '"toetra.replay-report-collection"' in probe
    assert '"-m",' in probe and '"toetra",' in probe
    assert "CLI artifacts \u03a9" in probe
    assert 'dataset := "reference data.csv"' in probe
    assert "from toetra.examples import credit_risk_policy" in probe
    assert 'find_spec("forml") is None' in probe
    assert 'find_spec("dsl") is None' in probe
    assert 'find_spec("model") is None' in probe
    assert "target := risk_score" in probe
    assert '"demo" / "quickstart" / "verify_model.py"' in probe
    assert '"quickstart-report.json"' in probe
    assert '"toetra.verification-report-collection"' in probe
    assert "demo-quickstart" in makefile
    assert "demo-regression" in makefile
    assert "demo-classification" in makefile
    assert "prepare_rc2_changelog" not in makefile
    assert "--require-clean" in makefile


def test_permanent_release_gates_cover_repository_boundaries() -> None:
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "repository-check:" in makefile
    assert "python scripts/repository/check_repository_contract.py" in makefile

    assert "demo-check: demo-quickstart demo-regression demo-classification" in makefile
    assert "release-check:" in makefile
    assert "review-bundle-check:" in makefile
    assert "outside-in-check:" in makefile
    assert "python scripts/release/check_outside_in.py" in makefile
    assert "public-surface-check:" in makefile
    assert "python scripts/release/check_public_surfaces.py" in makefile

    ci_target = re.search(r"^ci:.*$", makefile, flags=re.MULTILINE)
    local_target = re.search(r"^ci-local:.*$", makefile, flags=re.MULTILINE)
    assert ci_target is not None
    assert local_target is not None
    assert "repository-check" in ci_target.group(0)
    assert "repository-check" in local_target.group(0)
