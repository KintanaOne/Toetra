"""Run the reproducible end-to-end smoke scenario for the shipped Toetra CLI."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn, cast

FIXTURE_SOURCE = r"""
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
(root / "policy.toetra").write_text(
    'model := "linear model.joblib"\n'
    "target := score\n"
    'dataset := "reference data.csv"\n\n'
    "[BOUND]:\n"
    "forall x0\n"
    "with domain(x0.a: [0.0, 3.0])\n"
    "=> target[x0] <= 7.0 using Z3\n",
    encoding="utf-8",
)
(root / "witness.toetra").write_text(
    'model := "linear model.joblib"\n'
    "target := score\n"
    'dataset := "reference data.csv"\n\n'
    "[LOGIC]:\n"
    "exists x0\n"
    "with domain(x0.a: [0.0, 3.0])\n"
    "=> target[x0] == 5.0 using Z3\n",
    encoding="utf-8",
)
(root / "failure.toetra").write_text(
    'model := "linear model.joblib"\n'
    "target := score\n"
    'dataset := "reference data.csv"\n\n'
    "[BOUND]:\n"
    "forall x0\n"
    "with domain(x0.a: [0.0, 3.0])\n"
    "=> target[x0] < 0.0 using Z3\n",
    encoding="utf-8",
)
"""


class CliSmokeError(RuntimeError):
    """Raised when the reproducible CLI scenario violates its contract."""


@dataclass(frozen=True, slots=True)
class CliSmokeSummary:
    """Summary returned after one successful CLI smoke scenario."""

    version: str
    workspace: Path
    command_count: int


@dataclass(frozen=True, slots=True)
class _CommandResult:
    arguments: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


def project_version(repository: Path) -> str:
    """Return the version declared by one Toetra checkout."""

    payload = tomllib.loads((repository / "pyproject.toml").read_text(encoding="utf-8"))
    project = payload.get("project")
    if not isinstance(project, dict):
        raise CliSmokeError("pyproject.toml does not contain a [project] table.")
    version = project.get("version")
    if not isinstance(version, str) or not version:
        raise CliSmokeError("pyproject.toml does not declare a project version.")
    return version


def console_for_python(python: Path) -> Path:
    """Return the Toetra console script colocated with one Python executable."""

    python = _absolute_path(python)
    suffix = ".exe" if os.name == "nt" else ""
    console = python.parent / f"toetra{suffix}"
    if not console.is_file():
        raise CliSmokeError(
            f"Toetra console script not found next to {python}: {console}"
        )
    return console


def run_cli_smoke(
    *,
    python: Path,
    console: Path,
    expected_version: str,
    workspace_parent: Path | None = None,
    environment: Mapping[str, str] | None = None,
    keep_workspace: bool = False,
) -> CliSmokeSummary:
    """Exercise all five CLI commands through both supported entry points."""

    python = _absolute_path(python)
    console = _absolute_path(console)
    if not python.is_file():
        raise CliSmokeError(f"Python executable not found: {python}")
    if not console.is_file():
        raise CliSmokeError(f"Toetra console script not found: {console}")

    parent = (
        None if workspace_parent is None else workspace_parent.expanduser().resolve()
    )
    if parent is not None:
        parent.mkdir(parents=True, exist_ok=True)
    workspace = Path(tempfile.mkdtemp(prefix="toetra-cli-smoke-", dir=parent)).resolve()
    clean_environment = _clean_environment(environment)
    command_count = 0

    try:
        module = (str(python), "-I", "-m", "toetra")
        console_command = (str(console),)

        for prefix in (module, console_command):
            version_result = _run(
                (*prefix, "--version"),
                cwd=workspace,
                environment=clean_environment,
            )
            command_count += 1
            _expect_empty(version_result.stderr, label="version stderr")
            _expect_equal(
                version_result.stdout,
                f"toetra {expected_version}\n",
                label="CLI version",
            )

        _run(
            (str(python), "-I", "-c", FIXTURE_SOURCE, str(workspace)),
            cwd=workspace,
            environment=clean_environment,
        )
        command_count += 1

        policy = workspace / "policy.toetra"
        witness = workspace / "witness.toetra"
        failure = workspace / "failure.toetra"
        model = workspace / "linear model.joblib"
        dataset = workspace / "reference data.csv"
        candidate_model = workspace / "candidate model.joblib"
        candidate_dataset = workspace / "candidate reference.csv"

        generated = workspace / "generated policies" / "smoke policy.toetra"
        init_result = _run(
            (
                *console_command,
                "init",
                str(generated),
                "--model",
                str(model),
                "--target",
                "score",
                "--dataset",
                str(dataset),
            ),
            cwd=workspace,
            environment=clean_environment,
        )
        command_count += 1
        _expect_equal(
            init_result.stdout,
            f"{generated.resolve()}\n",
            label="init stdout",
        )
        _expect_empty(init_result.stderr, label="init stderr")
        generated_source = _read_text(generated)
        _require('model := "../linear model.joblib"' in generated_source, "init model")
        _require("target := score" in generated_source, "init target")
        _require(
            'dataset := "../reference data.csv"' in generated_source,
            "init dataset",
        )

        init_again = _run(
            (
                *module,
                "init",
                str(generated),
                "--model",
                str(model),
                "--target",
                "score",
                "--dataset",
                str(dataset),
            ),
            cwd=workspace,
            environment=clean_environment,
            expected_returncodes=(3,),
        )
        command_count += 1
        _expect_empty(init_again.stdout, label="second init stdout")
        _require("already exists" in init_again.stderr, "second init diagnostic")
        _expect_equal(
            _read_text(generated),
            generated_source,
            label="init preservation",
        )

        for level in ("syntax", "semantic", "executable"):
            validation = _run(
                (
                    *module,
                    "validate",
                    str(generated),
                    "--level",
                    level,
                    "--format",
                    "json",
                ),
                cwd=workspace,
                environment=clean_environment,
            )
            command_count += 1
            _expect_empty(validation.stderr, label=f"validate {level} stderr")
            validation_payload = _json_mapping(validation.stdout, f"validate {level}")
            _expect_equal(
                validation_payload.get("schema"),
                "toetra.validation-result",
                label=f"validate {level} schema",
            )
            _expect_equal(
                validation_payload.get("schema_version"),
                1,
                label=f"validate {level} schema version",
            )
            _expect_equal(
                validation_payload.get("valid"),
                True,
                label=f"validate {level} validity",
            )
            _expect_equal(
                validation_payload.get("completed_level"),
                level,
                label=f"validate {level} completion",
            )

        inspection_output = workspace / "outputs" / "inspection.json"
        inspection = _run(
            (
                *console_command,
                "inspect",
                str(generated),
                "--format",
                "json",
                "--output",
                str(inspection_output),
            ),
            cwd=workspace,
            environment=clean_environment,
        )
        command_count += 1
        _expect_empty(inspection.stdout, label="inspect stdout")
        _expect_empty(inspection.stderr, label="inspect stderr")
        inspection_payload = _json_file(inspection_output, "inspection")
        _expect_equal(
            inspection_payload.get("schema"),
            "toetra.inspection",
            label="inspection schema",
        )
        _expect_equal(
            inspection_payload.get("schema_version"),
            1,
            label="inspection schema version",
        )
        execution = _mapping(
            inspection_payload.get("execution"),
            "inspection execution",
        )
        _expect_equal(
            execution.get("translation_ready"),
            True,
            label="inspection translation readiness",
        )
        _reject_private_inspection_names(inspection_output)

        generated_report = workspace / "outputs" / "generated.json"
        artifact_directory = workspace / "artifacts"
        verification = _run(
            (
                *console_command,
                "verify",
                str(generated),
                "--format",
                "json",
                "--output",
                str(generated_report),
                "--artifacts-dir",
                str(artifact_directory),
                "--artifact-stem",
                "generated-smoke",
            ),
            cwd=workspace,
            environment=clean_environment,
        )
        command_count += 1
        _expect_empty(verification.stdout, label="verify stdout")
        _expect_empty(verification.stderr, label="verify stderr")
        generated_payload = _verification_payload(generated_report)
        _expect_report_status(generated_payload, "proved")
        _check_artifacts(
            artifact_directory,
            stem="generated-smoke",
            primary_json=generated_report,
            expected_process_status=0,
        )

        witness_report = workspace / "outputs" / "witness.json"
        witness_verification = _run(
            (
                *module,
                "verify",
                str(witness),
                "--format",
                "json",
                "--output",
                str(witness_report),
            ),
            cwd=workspace,
            environment=clean_environment,
        )
        command_count += 1
        _expect_empty(witness_verification.stdout, label="witness stdout")
        _expect_empty(witness_verification.stderr, label="witness stderr")
        _expect_report_status(_verification_payload(witness_report), "witness")

        witness_replay_output = workspace / "outputs" / "witness-replay.json"
        witness_replay = _run(
            (
                *console_command,
                "replay",
                str(witness_report),
                "--specification",
                str(witness),
                "--format",
                "json",
                "--output",
                str(witness_replay_output),
            ),
            cwd=workspace,
            environment=clean_environment,
        )
        command_count += 1
        _expect_empty(witness_replay.stdout, label="witness replay stdout")
        _expect_empty(witness_replay.stderr, label="witness replay stderr")
        _check_replay(witness_replay_output)

        failure_report = workspace / "outputs" / "failure.json"
        failed_verification = _run(
            (
                *module,
                "verify",
                str(failure),
                "--format",
                "json",
                "--output",
                str(failure_report),
            ),
            cwd=workspace,
            environment=clean_environment,
            expected_returncodes=(1,),
        )
        command_count += 1
        _expect_empty(failed_verification.stdout, label="failure stdout")
        _expect_empty(failed_verification.stderr, label="failure stderr")
        _expect_report_status(_verification_payload(failure_report), "counterexample")

        failure_replay_output = workspace / "outputs" / "failure-replay.json"
        failure_replay = _run(
            (
                *console_command,
                "replay",
                str(failure_report),
                "--specification",
                str(failure),
                "--format",
                "json",
                "--output",
                str(failure_replay_output),
            ),
            cwd=workspace,
            environment=clean_environment,
        )
        command_count += 1
        _expect_empty(failure_replay.stdout, label="failure replay stdout")
        _expect_empty(failure_replay.stderr, label="failure replay stderr")
        _check_replay(failure_replay_output)

        override_inspection_output = workspace / "outputs" / "override-inspection.json"
        override_inspection = _run(
            (
                *module,
                "inspect",
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
                str(override_inspection_output),
            ),
            cwd=workspace,
            environment=clean_environment,
        )
        command_count += 1
        _expect_empty(override_inspection.stdout, label="override inspect stdout")
        _expect_empty(override_inspection.stderr, label="override inspect stderr")
        override_inspection_payload = _json_file(
            override_inspection_output,
            "override inspection",
        )
        override_inspection_provenance = _mapping(
            override_inspection_payload.get("provenance"),
            "override inspection provenance",
        )
        _check_execution_context(
            _mapping(
                override_inspection_provenance.get("execution_context"),
                "override inspection execution context",
            ),
            candidate_model=candidate_model,
            candidate_dataset=candidate_dataset,
        )

        override_report = workspace / "outputs" / "override-verification.json"
        override_verification = _run(
            (
                *console_command,
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
                str(override_report),
            ),
            cwd=workspace,
            environment=clean_environment,
        )
        command_count += 1
        _expect_empty(override_verification.stdout, label="override verify stdout")
        _expect_empty(override_verification.stderr, label="override verify stderr")
        override_payload = _verification_payload(override_report)
        _expect_report_status(override_payload, "proved")
        provenance = _mapping(override_payload.get("provenance"), "override provenance")
        _check_execution_context(
            _mapping(provenance.get("execution_context"), "override execution context"),
            candidate_model=candidate_model,
            candidate_dataset=candidate_dataset,
        )

        temporary_files = tuple(
            path
            for path in workspace.rglob("*")
            if path.is_file() and ".tmp" in path.name
        )
        _require(not temporary_files, f"temporary files remain: {temporary_files}")

        summary = CliSmokeSummary(
            version=expected_version,
            workspace=workspace,
            command_count=command_count,
        )
    except Exception as error:
        raise CliSmokeError(
            f"CLI smoke failed; workspace retained at {workspace}: {error}"
        ) from error
    else:
        if not keep_workspace:
            try:
                shutil.rmtree(workspace)
            except OSError as error:
                raise CliSmokeError(
                    f"CLI smoke passed but cleanup failed for {workspace}: {error}"
                ) from error
        return summary


def _absolute_path(path: Path) -> Path:
    """Return an absolute path without dereferencing virtualenv symlinks."""

    return Path(os.path.abspath(os.fspath(path.expanduser())))


def _clean_environment(environment: Mapping[str, str] | None) -> dict[str, str]:
    clean = dict(os.environ if environment is None else environment)
    clean.pop("PYTHONPATH", None)
    clean["PYTHONSAFEPATH"] = "1"
    clean["PYTHONHASHSEED"] = "0"
    clean["OMP_NUM_THREADS"] = "1"
    clean["OPENBLAS_NUM_THREADS"] = "1"
    clean["MKL_NUM_THREADS"] = "1"
    return clean


def _run(
    arguments: Sequence[str],
    *,
    cwd: Path,
    environment: Mapping[str, str],
    expected_returncodes: tuple[int, ...] = (0,),
) -> _CommandResult:
    completed = subprocess.run(
        tuple(arguments),
        cwd=cwd,
        env=dict(environment),
        check=False,
        capture_output=True,
        text=True,
    )
    result = _CommandResult(
        arguments=tuple(arguments),
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
    if result.returncode not in expected_returncodes:
        raise CliSmokeError(
            "Unexpected command status.\n"
            f"command: {subprocess.list2cmdline(result.arguments)}\n"
            f"expected: {expected_returncodes}\n"
            f"actual: {result.returncode}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result


def _read_text(path: Path) -> str:
    if not path.is_file():
        raise CliSmokeError(f"Expected file was not created: {path}")
    return path.read_text(encoding="utf-8")


def _json_file(path: Path, label: str) -> dict[str, object]:
    return _json_mapping(_read_text(path), label)


def _json_mapping(raw: str, label: str) -> dict[str, object]:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as error:
        raise CliSmokeError(f"{label} is not valid JSON: {error}") from error
    return _mapping(payload, label)


def _mapping(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise CliSmokeError(f"{label} must be a JSON object, got {value!r}.")
    return cast(dict[str, object], value)


def _sequence(value: object, label: str) -> list[object]:
    if not isinstance(value, list):
        raise CliSmokeError(f"{label} must be a JSON array, got {value!r}.")
    return cast(list[object], value)


def _verification_payload(path: Path) -> dict[str, object]:
    payload = _json_file(path, "verification report")
    _expect_equal(
        payload.get("schema"),
        "toetra.verification-report-collection",
        label="verification schema",
    )
    _expect_equal(payload.get("schema_version"), 6, label="verification version")
    return payload


def _expect_report_status(payload: Mapping[str, object], expected: str) -> None:
    reports = _sequence(payload.get("reports"), "verification reports")
    _expect_equal(len(reports), 1, label="verification report count")
    report = _mapping(reports[0], "verification report")
    execution = _mapping(report.get("execution"), "verification execution")
    _expect_equal(execution.get("status"), expected, label="verification status")


def _check_replay(path: Path) -> None:
    payload = _json_file(path, "replay report")
    _expect_equal(
        payload.get("schema"),
        "toetra.replay-report-collection",
        label="replay schema",
    )
    _expect_equal(payload.get("schema_version"), 1, label="replay version")
    _expect_equal(payload.get("conclusion"), "consistent", label="replay conclusion")


def _check_artifacts(
    directory: Path,
    *,
    stem: str,
    primary_json: Path,
    expected_process_status: int,
) -> None:
    artifact_json = directory / f"{stem}.json"
    artifact_html = directory / f"{stem}.html"
    manifest_path = directory / f"{stem}.manifest.json"
    _expect_equal(
        primary_json.read_bytes(),
        artifact_json.read_bytes(),
        label="primary and artifact JSON",
    )
    _require(artifact_html.is_file(), f"HTML artifact missing: {artifact_html}")
    manifest = _json_file(manifest_path, "run manifest")
    _expect_equal(
        manifest.get("schema"),
        "toetra.run-manifest",
        label="manifest schema",
    )
    _expect_equal(manifest.get("schema_version"), 1, label="manifest version")
    _expect_equal(
        manifest.get("process_status"),
        expected_process_status,
        label="manifest process status",
    )
    artifacts = _mapping(manifest.get("artifacts"), "manifest artifacts")
    for role, path in (("json", artifact_json), ("html", artifact_html)):
        record = _mapping(artifacts.get(role), f"manifest {role} artifact")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        _expect_equal(record.get("sha256"), digest, label=f"{role} digest")


def _check_execution_context(
    context: Mapping[str, object],
    *,
    candidate_model: Path,
    candidate_dataset: Path,
) -> None:
    declared = _mapping(context.get("declared"), "declared execution context")
    effective = _mapping(context.get("effective"), "effective execution context")
    overrides = _mapping(context.get("overrides"), "execution overrides")
    _expect_equal(
        declared,
        {
            "model": "linear model.joblib",
            "target": "score",
            "dataset": "reference data.csv",
        },
        label="declared execution context",
    )
    _expect_equal(
        effective,
        {
            "model": str(candidate_model),
            "target": "risk_score",
            "dataset": str(candidate_dataset),
        },
        label="effective execution context",
    )
    _expect_equal(
        overrides,
        {"model": True, "target": True, "dataset": True},
        label="execution override flags",
    )


def _reject_private_inspection_names(path: Path) -> None:
    text = _read_text(path)
    forbidden = ("IR1", "IR2", "toetra._compiler", "ArithRef", "BoolRef")
    leaked = tuple(name for name in forbidden if name in text)
    _require(not leaked, f"inspection leaked private names: {leaked}")


def _expect_empty(value: str, *, label: str) -> None:
    _expect_equal(value, "", label=label)


def _expect_equal(actual: object, expected: object, *, label: str) -> None:
    if actual != expected:
        raise CliSmokeError(f"{label}: expected {expected!r}, got {actual!r}.")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CliSmokeError(message)


def _fail(message: str) -> NoReturn:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def main(argv: Sequence[str] | None = None) -> int:
    repository = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(
        description="Run the reproducible Toetra CLI end-to-end smoke scenario."
    )
    parser.add_argument(
        "--python",
        type=Path,
        default=Path(sys.executable),
        help="Python executable whose Toetra installation must be tested.",
    )
    parser.add_argument(
        "--console",
        type=Path,
        help="Toetra console script; defaults to the script beside --python.",
    )
    parser.add_argument(
        "--expected-version",
        default=project_version(repository),
        help="Expected CLI version; defaults to pyproject.toml.",
    )
    parser.add_argument(
        "--workspace-parent",
        type=Path,
        help="Optional parent for the temporary smoke workspace.",
    )
    parser.add_argument(
        "--keep-workspace",
        action="store_true",
        help="Keep the temporary workspace after a successful run.",
    )
    arguments = parser.parse_args(argv)

    python = _absolute_path(arguments.python)
    try:
        console = (
            console_for_python(python)
            if arguments.console is None
            else _absolute_path(arguments.console)
        )
        summary = run_cli_smoke(
            python=python,
            console=console,
            expected_version=arguments.expected_version,
            workspace_parent=arguments.workspace_parent,
            keep_workspace=arguments.keep_workspace,
        )
    except CliSmokeError as error:
        _fail(str(error))

    print(
        "Toetra CLI smoke passed: "
        f"version={summary.version}, commands={summary.command_count}."
    )
    if arguments.keep_workspace:
        print(f"Workspace retained at {summary.workspace}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
