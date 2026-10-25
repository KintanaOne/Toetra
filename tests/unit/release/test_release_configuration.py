from __future__ import annotations

import re
import shlex
import subprocess
import tomllib
from itertools import product
from pathlib import Path

import pytest
import yaml

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
    # BaseLoader preserves GitHub's `on` key instead of treating it as YAML 1.1 true.
    workflow = yaml.load(
        (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8"),
        Loader=yaml.BaseLoader,
    )
    assert workflow["on"]["push"]["branches"] == ["main"]
    assert "pull_request" in workflow["on"]
    jobs = workflow["jobs"]
    assert set(jobs["quality"]["strategy"]["matrix"]["python-version"]) == {
        "3.11",
        "3.12",
    }
    installation = jobs["install"]
    matrix = installation["strategy"]["matrix"]
    assert not matrix.get("exclude") and not matrix.get("include")
    cells = set(product(matrix["os"], matrix["python-version"], matrix["distribution"]))
    assert cells == set(
        product(
            ("ubuntu-latest", "windows-latest"), ("3.11", "3.12"), ("wheel", "sdist")
        )
    )
    assert installation["runs-on"] == "${{ matrix.os }}"
    assert installation["needs"] == "release"
    assert jobs["release"]["needs"] == "quality"
    assert installation["strategy"]["fail-fast"] == "false"
    for job in jobs.values():
        assert 0 < int(job["timeout-minutes"]) <= 45
        assert job.get("continue-on-error", "false") == "false"
        assert all(
            step.get("continue-on-error", "false") == "false" for step in job["steps"]
        )

    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "dist/toetra_review_bundle.zip" in makefile


def test_installation_jobs_consume_the_single_build_without_rebuilding_sources() -> (
    None
):
    workflow = yaml.load(
        (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8"),
        Loader=yaml.BaseLoader,
    )
    release = workflow["jobs"]["release"]["steps"]
    installation = workflow["jobs"]["install"]["steps"]
    uploads = [
        step
        for step in release
        if step.get("uses", "").startswith("actions/upload-artifact@")
    ]
    downloads = [
        step
        for step in installation
        if step.get("uses", "").startswith("actions/download-artifact@")
    ]
    assert len(uploads) == len(downloads) == 1
    upload, download = uploads[0]["with"], downloads[0]["with"]
    assert upload["name"] == download["name"]
    assert upload["if-no-files-found"] == "error"
    assert download["digest-mismatch"] == "error"
    assert not {"run-id", "repository", "github-token"} & download.keys()
    assert {"dist/*.whl", "dist/*.tar.gz", "dist/SHA256SUMS"} <= set(
        upload["path"].splitlines()
    )
    release_commands = "\n".join(step.get("run", "") for step in release)
    assert "make dist dist-check" in release_commands
    assert "make demo-check" in release_commands
    assert "make review-bundle-check" in release_commands
    install_commands = "\n".join(step.get("run", "") for step in installation)
    assert "build_distribution.py" not in install_commands
    assert not re.search(r"^\s*make(?:\s|$)", install_commands, re.MULTILINE)
    assert (
        "check_installed_distribution.py dist --format ${{ matrix.distribution }}"
        in install_commands
    )
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    requirements = project["project"]["optional-dependencies"]["dev"]
    host_installs = [
        shlex.split(step["run"])[4:]
        for step in installation
        if step.get("run", "").startswith("python -m pip install ")
    ]
    assert host_installs == [
        [next(item for item in requirements if item.startswith("packaging=="))]
    ]


@pytest.mark.parametrize("status", ("", " M changed.py\n"))
def test_native_windows_checkout_guard_fails_for_mutations(
    monkeypatch: pytest.MonkeyPatch, status: str
) -> None:
    workflow = yaml.load(
        (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8"),
        Loader=yaml.BaseLoader,
    )
    guards = [
        step
        for step in workflow["jobs"]["install"]["steps"]
        if step.get("if") == "always()"
    ]
    assert len(guards) == 1
    guard = guards[0]
    assert guard["shell"] == "python"
    monkeypatch.setattr(subprocess, "check_output", lambda *args, **kwargs: status)
    source = compile(guard["run"], "installation-checkout-guard", "exec")
    if status:
        with pytest.raises(SystemExit, match="modified the checkout"):
            exec(source, {})
    else:
        exec(source, {})


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


def test_typing_marker_is_empty_and_explicitly_packaged() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    manifest = (ROOT / "MANIFEST.in").read_text(encoding="utf-8")

    assert (ROOT / "src" / "toetra" / "py.typed").read_bytes() == b""
    assert project["tool"]["setuptools"]["package-data"]["toetra"] == ["py.typed"]
    assert "include src/toetra/py.typed" in manifest.splitlines()


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
    smoke = (ROOT / "scripts" / "ci" / "check_cli_smoke.py").read_text(encoding="utf-8")
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "LogisticRegression" in probe
    assert "target[applicant].label" in probe
    assert "target[applicant].probability" in probe
    assert "VerificationStatus.WITNESS" in probe
    assert "run_cli_smoke" in probe
    assert '"validate"' in smoke
    assert '"inspect"' in smoke
    assert '"verify"' in smoke
    assert '"replay"' in smoke
    assert '"init"' in smoke
    assert '"toetra.validation-result"' in smoke
    assert '"toetra.inspection"' in smoke
    assert '"toetra.replay-report-collection"' in smoke
    assert '"-m", "toetra"' in smoke
    assert "toetra-cli-smoke-" in smoke
    assert 'dataset := "reference data.csv"' in smoke
    assert 'dataset := "../reference data.csv"' in smoke
    assert '"generated policies"' in smoke
    assert "from toetra.examples import credit_risk_policy" in probe
    assert 'find_spec("forml") is None' in probe
    assert 'find_spec("dsl") is None' in probe
    assert 'find_spec("model") is None' in probe
    assert "target := risk_score" in probe
    assert '"demo" / "quickstart" / "verify_model.py"' in probe
    assert '"quickstart-report.json"' in probe
    assert '"toetra.verification-report-collection"' in probe
    assert "cli-smoke-check" in makefile
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
