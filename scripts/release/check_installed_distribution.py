"""Install the built wheel outside the checkout and probe the public API."""

from __future__ import annotations

import argparse
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
