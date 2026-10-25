"""Install built wheel/sdist archives outside the checkout and probe the public API."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
import venv
from collections.abc import Sequence
from pathlib import Path

PROBE = r"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression

import toetra
from toetra import VerificationSession, VerificationStatus, verify
from toetra.examples import credit_risk_policy

module_path = Path(toetra.__file__).resolve()
expected_public_api = (
    "CounterexampleReplay",
    "ReplayUnavailableError",
    "VerificationConfigurationError",
    "VerificationFinding",
    "VerificationReport",
    "VerificationRuntimeError",
    "VerificationSession",
    "VerificationStatus",
    "verify",
)
assert toetra.__all__ == expected_public_api

initial_public_names = {
    name for name in vars(toetra) if not name.startswith("_")
}
allowed_public_names = {*expected_public_api, "examples"}

assert initial_public_names <= allowed_public_names
assert {
    "VerificationSession",
    "VerificationStatus",
    "verify",
    "examples",
} <= initial_public_names

for name in expected_public_api:
    assert getattr(toetra, name) is not None

assert {name for name in vars(toetra) if not name.startswith("_")} == (
    allowed_public_names
)
assert importlib.util.find_spec("forml") is None
assert importlib.util.find_spec("dsl") is None
assert importlib.util.find_spec("model") is None
assert "site-packages" in module_path.parts, module_path
assert (module_path.parent / "py.typed").is_file()
assert callable(verify)
assert VerificationSession is not None
policy_source = credit_risk_policy()
assert "target := risk_score" in policy_source
assert "exists applicant" in policy_source

spec = importlib.util.find_spec("toetra._language.grammar")
assert spec is not None and spec.submodule_search_locations
root = Path(next(iter(spec.submodule_search_locations)))
assert (root / "toetra_grammar.ebnf").is_file()
assert (root / "toetra_grammar.lark").is_file()
with TemporaryDirectory(prefix="toetra-installed-classification-") as raw_directory:
    directory = Path(raw_directory)
    frame = pd.DataFrame(
        {
            "income": [-6.0, -5.0, -4.0, -3.0, 3.0, 4.0, 5.0, 6.0],
            "decision": ["no", "no", "no", "no", "yes", "yes", "yes", "yes"],
        }
    )
    model = LogisticRegression(random_state=0, max_iter=1000).fit(
        frame[["income"]], frame["decision"]
    )
    model_path = directory / "binary.joblib"
    dataset_path = directory / "binary.csv"
    policy_path = directory / "policy.toetra"
    joblib.dump(model, model_path)
    frame.to_csv(dataset_path, index=False)
    policy_path.write_text(
        '''model := "binary.joblib"
target := decision

[LOGIC]:
forall applicant
with domain(applicant.income: [-6.0, -3.0])
=> target[applicant].label == "no" using Z3

[LOGIC]:
exists applicant
with domain(applicant.income: [3.0, 6.0])
=> target[applicant].probability("yes") >= 0.80 using Z3
''',
        encoding="utf-8",
    )
    session = verify(policy_path, model=model_path, dataset=dataset_path)
    assert tuple(report.status for report in session.reports) == (
        VerificationStatus.PROVED,
        VerificationStatus.WITNESS,
    )
    witness = session.first_witness
    assert witness is not None and witness.replay().is_consistent

print(f"Installed Toetra regression/classification probe passed from {module_path}")
"""

TYPED_CONSUMER = """\
from typing import assert_type

from toetra import VerificationSession, VerificationStatus, verify


def check_policy(specification: str) -> VerificationSession:
    session = verify(specification)
    assert_type(session, VerificationSession)
    assert_type(session.reports[0].status, VerificationStatus)
    assert_type(session.exit_code, int)
    status: VerificationStatus = session.reports[0].status
    if status is VerificationStatus.PROVED:
        assert_type(session.to_text(), str)
    return session
"""


def installation_artifacts(
    directory: Path,
    *,
    format: str = "wheel",
    repository: Path | None = None,
) -> tuple[Path, ...]:
    """Select validated archives; never substitute a checkout or another format."""

    from scripts.release.distribution import (
        DistributionContractError,
        check_distribution_directory,
    )

    if format not in {"wheel", "sdist", "both"}:
        raise DistributionContractError(f"Unsupported installation format: {format!r}")
    artifacts = check_distribution_directory(directory.resolve(), repository=repository)
    if format == "both":
        return artifacts.wheel, artifacts.sdist
    return (artifacts.wheel if format == "wheel" else artifacts.sdist,)


def _require_installed_location(package: Path, python: Path, *, probe: str) -> None:
    package = package.resolve()
    venv_root = python.parent.parent.resolve()
    if not package.is_relative_to(venv_root) or "site-packages" not in package.parts:
        raise RuntimeError(f"{probe} resolved Toetra outside the clean venv: {package}")


def check_installed_origin(
    python: Path, workspace: Path, *, environment: dict[str, str]
) -> None:
    """Require the imported module to belong to this exact fresh environment."""

    completed = subprocess.run(
        [str(python), "-I", "-c", "import toetra; print(toetra.__file__)"],
        cwd=workspace,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    module_path = Path(completed.stdout.strip()).resolve()
    _require_installed_location(module_path.parent, python, probe="Import")
    print(f"Installed Toetra import: {module_path}")


def check_installed_typing(
    python: Path,
    workspace: Path,
    *,
    environment: dict[str, str],
) -> None:
    """Check a consumer and the installed facade without checkout search paths."""

    # The completeness verifier also discovers Python from PATH.
    environment = {
        **environment,
        "PATH": str(python.parent) + os.pathsep + environment.get("PATH", ""),
        "VIRTUAL_ENV": str(python.parent.parent),
    }
    (workspace / "consumer.py").write_text(TYPED_CONSUMER, encoding="utf-8")
    configuration = workspace / "pyrightconfig.json"
    configuration.write_text(
        json.dumps(
            {
                "include": ["consumer.py"],
                "typeCheckingMode": "strict",
                "extraPaths": [],
                "executionEnvironments": [{"root": ".", "extraPaths": []}],
            }
        ),
        encoding="utf-8",
    )
    command = [str(python), "-I", "-m", "pyright", "--pythonpath", str(python)]
    subprocess.run(
        [*command, "--project", str(configuration)],
        cwd=workspace,
        env=environment,
        check=True,
    )
    completed = subprocess.run(
        [*command, "--verifytypes", "toetra", "--ignoreexternal", "--outputjson"],
        cwd=workspace,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    result = json.loads(completed.stdout)
    completeness = result["typeCompleteness"]
    installed_root = Path(completeness["packageRootDirectory"]).resolve()
    _require_installed_location(installed_root, python, probe="Pyright")
    if completed.returncode or completeness["completenessScore"] != 1:
        failures = [
            {"name": symbol["name"], "diagnostics": symbol["diagnostics"]}
            for symbol in completeness["symbols"]
            if not symbol["isTypeKnown"]
        ]
        raise RuntimeError(f"Installed Toetra type completeness failed: {failures}")
    print(
        "Installed Toetra type completeness: 100%; "
        f"symbols={completeness['exportedSymbolCounts']}; package={installed_root}"
    )


def _venv_script(directory: Path, name: str) -> Path:
    if os.name == "nt":
        return directory / "Scripts" / f"{name}.exe"
    return directory / "bin" / name


def _venv_python(directory: Path) -> Path:
    if os.name == "nt":
        return directory / "Scripts" / "python.exe"
    return directory / "bin" / "python"


def check_installed_archive(
    archive: Path, *, repository_root: Path, pyright_requirement: str
) -> None:
    """Run the same isolated installed-package journey for either archive format."""

    from scripts.ci.check_cli_smoke import project_version, run_cli_smoke

    print(f"Checking installed archive: {archive.name}", flush=True)
    with tempfile.TemporaryDirectory(prefix="toetra-install-check-") as raw_directory:
        root = Path(raw_directory)
        environment = root / "venv"
        venv.EnvBuilder(with_pip=True, clear=True).create(environment)
        python = _venv_python(environment)
        clean_environment = os.environ.copy()
        clean_environment.pop("PYTHONPATH", None)
        clean_environment.pop("PYTHONHOME", None)
        clean_environment["PYTHONSAFEPATH"] = "1"
        clean_environment["VIRTUAL_ENV"] = str(environment)
        clean_environment["PATH"] = (
            str(python.parent) + os.pathsep + clean_environment.get("PATH", "")
        )
        subprocess.run(
            [
                str(python),
                "-I",
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                str(archive),
                pyright_requirement,
            ],
            check=True,
            cwd=root,
            env=clean_environment,
        )
        subprocess.run(
            [str(python), "-I", "-m", "pip", "check"],
            check=True,
            cwd=root,
            env=clean_environment,
        )
        check_installed_origin(python, root, environment=clean_environment)
        subprocess.run(
            [str(python), "-I", "-c", PROBE],
            check=True,
            cwd=root,
            env=clean_environment,
        )
        check_installed_typing(python, root, environment=clean_environment)

        console = _venv_script(environment, "toetra")
        run_cli_smoke(
            python=python,
            console=console,
            expected_version=project_version(repository_root),
            workspace_parent=root,
            environment=clean_environment,
        )

        quickstart = root / "verify_model.py"
        report = root / "quickstart-report.json"
        shutil.copy2(
            repository_root / "demo" / "quickstart" / "verify_model.py",
            quickstart,
        )
        subprocess.run(
            [
                str(python),
                "-I",
                str(quickstart),
                "--demo",
                "--json-output",
                str(report),
            ],
            check=True,
            cwd=root,
            env=clean_environment,
        )
        payload = json.loads(report.read_text(encoding="utf-8"))
        assert payload["schema"] == "toetra.verification-report-collection"
        assert payload["schema_version"] == 6
    print(f"Installed archive passed: {archive.name}", flush=True)


def main(argv: Sequence[str] | None = None) -> int:
    repository_root = Path(__file__).resolve().parents[2]
    if str(repository_root) not in sys.path:
        sys.path.insert(0, str(repository_root))

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", nargs="?", type=Path, default=Path("dist"))
    parser.add_argument(
        "--format",
        choices=("wheel", "sdist", "both"),
        default="wheel",
        help="Archive format to install; 'both' uses two separate fresh environments.",
    )
    arguments = parser.parse_args(argv)
    archives = installation_artifacts(
        arguments.directory, format=arguments.format, repository=repository_root
    )
    project = tomllib.loads(
        (repository_root / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]
    pyright_requirement = next(
        requirement
        for requirement in project["optional-dependencies"]["dev"]
        if requirement.startswith("pyright==")
    )
    for archive in archives:
        check_installed_archive(
            archive,
            repository_root=repository_root,
            pyright_requirement=pyright_requirement,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
