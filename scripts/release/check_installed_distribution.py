"""Install the built wheel outside the checkout and probe the public API."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import venv
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

CLI_FIXTURE = r"""
from __future__ import annotations

import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression

root = Path(sys.argv[1])
root.mkdir(parents=True, exist_ok=True)
frame = pd.DataFrame(
    {
        "a": [0.0, 1.0, 2.0, 3.0],
        "score": [1.0, 3.0, 5.0, 7.0],
        "risk_score": [1.0, 3.0, 5.0, 7.0],
    }
)
model = LinearRegression().fit(frame[["a"]], frame["score"])
joblib.dump(model, root / "linear model.joblib")
joblib.dump(model, root / "candidate model.joblib")
frame.to_csv(root / "reference data.csv", index=False)
frame.to_csv(root / "candidate reference.csv", index=False)
source = (
    'model := "linear model.joblib"\n'
    'target := score\n'
    'dataset := "reference data.csv"\n\n'
    '[BOUND]:\n'
    'forall x0\n'
    'with domain(x0.a: [0.0, 3.0])\n'
    '=> target[x0] <= 7.0 using Z3\n'
)
(root / "policy.toetra").write_text(source, encoding="utf-8")
failure_source = (
    'model := "linear model.joblib"\n'
    "target := score\n"
    'dataset := "reference data.csv"\n\n'
    "[BOUND]:\n"
    "forall x0\n"
    "with domain(x0.a: [0.0, 3.0])\n"
    "=> target[x0] < 0.0 using Z3\n"
)
(root / "failure.toetra").write_text(failure_source, encoding="utf-8")
"""


def _venv_script(directory: Path, name: str) -> Path:
    if os.name == "nt":
        return directory / "Scripts" / f"{name}.exe"
    return directory / "bin" / name


def _venv_python(directory: Path) -> Path:
    if os.name == "nt":
        return directory / "Scripts" / "python.exe"
    return directory / "bin" / "python"


def main() -> int:
    repository_root = Path(__file__).resolve().parents[2]
    if str(repository_root) not in sys.path:
        sys.path.insert(0, str(repository_root))
    from scripts.release.distribution import check_distribution_directory

    parser = argparse.ArgumentParser()
    parser.add_argument("directory", nargs="?", type=Path, default=Path("dist"))
    arguments = parser.parse_args()
    artifacts = check_distribution_directory(
        arguments.directory.resolve(), repository=repository_root
    )

    with tempfile.TemporaryDirectory(prefix="toetra-install-check-") as raw_directory:
        root = Path(raw_directory)
        environment = root / "venv"
        venv.EnvBuilder(with_pip=True, clear=True).create(environment)
        python = _venv_python(environment)
        subprocess.run(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                str(artifacts.wheel),
            ],
            check=True,
            cwd=root,
        )
        subprocess.run([str(python), "-m", "pip", "check"], check=True, cwd=root)
        clean_environment = os.environ.copy()
        clean_environment.pop("PYTHONPATH", None)
        clean_environment["PYTHONSAFEPATH"] = "1"
        subprocess.run(
            [str(python), "-I", "-c", PROBE],
            check=True,
            cwd=root,
            env=clean_environment,
        )

        cli_root = root / "CLI artifacts Ω"
        subprocess.run(
            [str(python), "-I", "-c", CLI_FIXTURE, str(cli_root)],
            check=True,
            cwd=root,
            env=clean_environment,
        )
        console = _venv_script(environment, "toetra")
        policy = cli_root / "policy.toetra"
        dataset = cli_root / "reference data.csv"
        candidate_model = cli_root / "candidate model.joblib"
        candidate_dataset = cli_root / "candidate reference.csv"
        validate = subprocess.run(
            [
                str(console),
                "validate",
                str(policy),
                "--format",
                "json",
            ],
            check=False,
            cwd=root,
            env=clean_environment,
            capture_output=True,
            text=True,
        )
        assert validate.returncode == 0, validate.stderr
        assert validate.stderr == ""
        validation_payload = json.loads(validate.stdout)
        assert validation_payload["schema"] == "toetra.validation-result"
        assert validation_payload["schema_version"] == 1
        assert validation_payload["valid"] is True
        assert validation_payload["completed_level"] == "executable"
        assert validation_payload["declarations"]["dataset"] == ("reference data.csv")
        assert validation_payload["effective"] == {
            "model": "linear model.joblib",
            "target": "score",
            "dataset": "reference data.csv",
        }
        assert validation_payload["overrides"] == {
            "model": False,
            "target": False,
            "dataset": False,
        }

        inspection_output = cli_root / "nested output" / "inspection.json"
        inspect = subprocess.run(
            [
                str(python),
                "-I",
                "-m",
                "toetra",
                "inspect",
                str(policy),
                "--format",
                "json",
                "--output",
                str(inspection_output),
            ],
            check=False,
            cwd=root,
            env=clean_environment,
            capture_output=True,
            text=True,
        )
        assert inspect.returncode == 0, inspect.stderr
        assert inspect.stdout == ""
        assert inspect.stderr == ""
        inspection_payload = json.loads(inspection_output.read_text(encoding="utf-8"))
        assert inspection_payload["schema"] == "toetra.inspection"
        assert inspection_payload["schema_version"] == 1
        assert inspection_payload["execution"]["translation_ready"] is True
        assert inspection_payload["model"]["dataset"]["declared_reference"] == (
            "reference data.csv"
        )
        assert inspection_payload["model"]["dataset"]["path"] == str(dataset)
        assert inspection_payload["model"]["dataset"]["overridden"] is False
        assert inspection_payload["specification"]["effective"]["target"] == "score"
        assert inspection_payload["specification"]["overrides"]["target"] is False

        verification_output = cli_root / "nested output" / "verification.json"
        artifact_directory = cli_root / "verification artifacts"

        verify_result = subprocess.run(
            [
                str(console),
                "verify",
                str(policy),
                "--model",
                str(candidate_model),
                "--target",
                "risk_score",
                "--dataset",
                str(candidate_dataset),
                "--format",
                "json",
                "--output",
                str(verification_output),
                "--artifacts-dir",
                str(artifact_directory),
                "--artifact-stem",
                "installed-check",
            ],
            check=False,
            cwd=root,
            env=clean_environment,
            capture_output=True,
            text=True,
        )

        assert verify_result.returncode == 0, verify_result.stderr
        assert verify_result.stdout == ""
        assert verify_result.stderr == ""

        verification_payload = json.loads(
            verification_output.read_text(encoding="utf-8")
        )
        assert verification_payload["schema"] == (
            "toetra.verification-report-collection"
        )
        assert verification_payload["schema_version"] == 6
        execution_context = verification_payload["provenance"]["execution_context"]
        assert execution_context["declared"] == {
            "model": "linear model.joblib",
            "target": "score",
            "dataset": "reference data.csv",
        }
        assert execution_context["effective"] == {
            "model": str(candidate_model),
            "target": "risk_score",
            "dataset": str(candidate_dataset),
        }
        assert execution_context["overrides"] == {
            "model": True,
            "target": True,
            "dataset": True,
        }

        artifact_json = artifact_directory / "installed-check.json"
        artifact_html = artifact_directory / "installed-check.html"

        assert verification_output.read_bytes() == artifact_json.read_bytes()

        artifact_manifest = artifact_directory / "installed-check.manifest.json"
        manifest_payload = json.loads(artifact_manifest.read_text(encoding="utf-8"))

        assert manifest_payload["schema"] == "toetra.run-manifest"
        assert manifest_payload["schema_version"] == 1
        assert manifest_payload["process_status"] == 0
        assert manifest_payload["execution_context"] == execution_context

        for role, artifact_path in (
            ("json", artifact_json),
            ("html", artifact_html),
        ):
            content = artifact_path.read_bytes()
            assert (
                manifest_payload["artifacts"][role]["sha256"]
                == hashlib.sha256(content).hexdigest()
            )

        failure_report = cli_root / "nested output" / "failure.json"
        failure = subprocess.run(
            [
                str(python),
                "-I",
                "-m",
                "toetra",
                "verify",
                str(cli_root / "failure.toetra"),
                "--dataset",
                str(dataset),
                "--format",
                "json",
                "--output",
                str(failure_report),
            ],
            check=False,
            cwd=root,
            env=clean_environment,
            capture_output=True,
            text=True,
        )

        assert failure.returncode == 1, failure.stderr
        assert failure.stdout == ""
        assert failure.stderr == ""

        failure_payload = json.loads(failure_report.read_text(encoding="utf-8"))
        assert failure_payload["schema_version"] == 6

        replay_output = cli_root / "nested output" / "replay.json"
        replay = subprocess.run(
            [
                str(console),
                "replay",
                str(failure_report),
                "--specification",
                str(cli_root / "failure.toetra"),
                "--format",
                "json",
                "--output",
                str(replay_output),
            ],
            check=False,
            cwd=root,
            env=clean_environment,
            capture_output=True,
            text=True,
        )

        assert replay.returncode == 0, (
            f"Replay returned {replay.returncode}\n"
            f"stdout:\n{replay.stdout}\n"
            f"stderr:\n{replay.stderr}"
        )
        assert replay.stdout == ""
        assert replay.stderr == ""
        replay_payload = json.loads(replay_output.read_text(encoding="utf-8"))
        assert replay_payload["schema"] == "toetra.replay-report-collection"
        assert replay_payload["schema_version"] == 1
        assert replay_payload["conclusion"] == "consistent"

        generated = cli_root / "generated policies" / "smoke policy.toetra"
        init_result = subprocess.run(
            [
                str(console),
                "init",
                str(generated),
                "--model",
                str(cli_root / "linear model.joblib"),
                "--target",
                "score",
                "--dataset",
                str(dataset),
            ],
            check=False,
            cwd=root,
            env=clean_environment,
            capture_output=True,
            text=True,
        )
        assert init_result.returncode == 0, init_result.stderr
        assert init_result.stdout == f"{generated.resolve()}\n"
        assert init_result.stderr == ""
        generated_source = generated.read_text(encoding="utf-8")
        assert 'model := "../linear model.joblib"' in generated_source
        assert "target := score" in generated_source
        assert 'dataset := "../reference data.csv"' in generated_source

        init_again = subprocess.run(
            [
                str(console),
                "init",
                str(generated),
                "--model",
                str(cli_root / "linear model.joblib"),
                "--target",
                "score",
                "--dataset",
                str(dataset),
            ],
            check=False,
            cwd=root,
            env=clean_environment,
            capture_output=True,
            text=True,
        )
        assert init_again.returncode == 3
        assert init_again.stdout == ""
        assert "already exists" in init_again.stderr
        assert generated.read_text(encoding="utf-8") == generated_source

        generated_validation = subprocess.run(
            [
                str(python),
                "-I",
                "-m",
                "toetra",
                "validate",
                str(generated),
                "--format",
                "json",
            ],
            check=False,
            cwd=root,
            env=clean_environment,
            capture_output=True,
            text=True,
        )
        assert generated_validation.returncode == 0, generated_validation.stderr
        assert generated_validation.stderr == ""
        assert json.loads(generated_validation.stdout)["valid"] is True

        generated_verification = subprocess.run(
            [
                str(console),
                "verify",
                str(generated),
                "--format",
                "json",
            ],
            check=False,
            cwd=root,
            env=clean_environment,
            capture_output=True,
            text=True,
        )
        assert generated_verification.returncode == 0, (
            f"Generated verification returned "
            f"{generated_verification.returncode}\n"
            f"stdout:\n{generated_verification.stdout}\n"
            f"stderr:\n{generated_verification.stderr}"
        )
        assert generated_verification.stderr == ""
        generated_payload = json.loads(generated_verification.stdout)
        assert generated_payload["schema_version"] == 6
        assert generated_payload["reports"][0]["status"] == "PROVED"

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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
