from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import joblib
import pandas as pd
import pytest
from sklearn.linear_model import LinearRegression

from toetra._backends.errors import BackendTranslationError
from toetra._cli.main import EXIT_OK, EXIT_RUNTIME, EXIT_USAGE, main

_SOURCE = """model := "linear.joblib"
target := score

[BOUND]:
forall x0
with domain(x0.a: [0.0, 3.0])
=> target[x0] <= 7.0 using Z3
"""


def _artifacts(tmp_path: Path) -> tuple[Path, Path, Path]:
    frame = pd.DataFrame(
        {
            "a": [0.0, 1.0, 2.0, 3.0],
            "score": [1.0, 3.0, 5.0, 7.0],
        }
    )
    model = LinearRegression().fit(frame[["a"]], frame["score"])
    model_path = tmp_path / "linear.joblib"
    dataset_path = tmp_path / "linear.csv"
    specification_path = tmp_path / "policy.toetra"
    joblib.dump(model, model_path)
    frame.to_csv(dataset_path, index=False)
    specification_path.write_text(_SOURCE, encoding="utf-8")
    return specification_path, model_path, dataset_path


def test_validate_syntax_json_needs_no_model(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    specification_path = tmp_path / "policy.toetra"
    specification_path.write_text(_SOURCE, encoding="utf-8")

    assert (
        main(
            [
                "validate",
                str(specification_path),
                "--level",
                "syntax",
                "--format",
                "json",
            ]
        )
        == EXIT_OK
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["schema"] == "toetra.validation-result"
    assert payload["valid"] is True
    assert payload["completed_level"] == "syntax"
    assert captured.err == ""


def test_negative_validation_remains_primary_json_output(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    specification_path = tmp_path / "invalid.toetra"
    specification_path.write_text("not a Toetra program", encoding="utf-8")

    assert (
        main(
            [
                "validate",
                str(specification_path),
                "--level",
                "syntax",
                "--format",
                "json",
            ]
        )
        == EXIT_USAGE
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["valid"] is False
    assert payload["diagnostics"]
    assert captured.err == ""


def test_validate_rejects_execution_options_for_semantic_level(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    specification_path = tmp_path / "policy.toetra"
    specification_path.write_text(_SOURCE, encoding="utf-8")

    assert (
        main(
            [
                "validate",
                str(specification_path),
                "--level",
                "semantic",
                "--timeout-ms",
                "1000",
            ]
        )
        == EXIT_USAGE
    )

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "require '--level executable'" in captured.err


def test_inspect_writes_atomic_json_without_stdout(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    specification_path, _, dataset_path = _artifacts(tmp_path)
    output = tmp_path / "nested" / "inspection.json"

    assert (
        main(
            [
                "inspect",
                str(specification_path),
                "--dataset",
                str(dataset_path),
                "--format",
                "json",
                "--output",
                str(output),
            ]
        )
        == EXIT_OK
    )

    captured = capsys.readouterr()
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["schema"] == "toetra.inspection"
    assert payload["execution"]["policy"]["timeout_ms"] == 30_000
    assert captured.out == ""
    assert captured.err == ""
    assert not tuple(output.parent.glob(".*.tmp"))


def test_inspect_no_timeout_is_reflected_in_plan(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    specification_path, _, dataset_path = _artifacts(tmp_path)

    assert (
        main(
            [
                "inspect",
                str(specification_path),
                "--dataset",
                str(dataset_path),
                "--no-timeout",
                "--format",
                "json",
            ]
        )
        == EXIT_OK
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["execution"]["policy"]["timeout_ms"] is None
    assert captured.err == ""


def test_output_cannot_overwrite_specification(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    specification_path = tmp_path / "policy.toetra"
    specification_path.write_text(_SOURCE, encoding="utf-8")

    assert (
        main(
            [
                "validate",
                str(specification_path),
                "--level",
                "syntax",
                "--output",
                str(specification_path),
            ]
        )
        == EXIT_USAGE
    )

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "collides with a consumed input" in captured.err
    assert specification_path.read_text(encoding="utf-8") == _SOURCE


def test_validate_semantic_resolves_model_without_backend_translation(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    specification_path, _, dataset_path = _artifacts(tmp_path)

    def fail_if_translated(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("semantic validation must not translate a backend task")

    monkeypatch.setattr(
        "toetra._backends.z3_backend.runner.Z3Runner.translate",
        fail_if_translated,
    )

    assert (
        main(
            [
                "validate",
                str(specification_path),
                "--dataset",
                str(dataset_path),
                "--level",
                "semantic",
                "--format",
                "json",
            ]
        )
        == EXIT_OK
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["completed_level"] == "semantic"
    assert payload["valid"] is True
    assert captured.err == ""


def test_inspect_failure_uses_one_json_stderr_diagnostic(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    missing = tmp_path / "missing.toetra"

    assert (
        main(
            [
                "--diagnostic-format",
                "json",
                "inspect",
                str(missing),
            ]
        )
        == EXIT_USAGE
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.err)
    assert captured.out == ""
    assert payload["schema"] == "toetra.cli-diagnostic"
    assert payload["schema_version"] == 1
    assert payload["code"] == "SPECIFICATION_NOT_FOUND"
    assert payload["command"] == "inspect"


def test_cli_rejects_non_toetra_specification_extension(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    specification_path = tmp_path / "policy.txt"
    specification_path.write_text(_SOURCE, encoding="utf-8")

    assert main(["validate", str(specification_path), "--level", "syntax"]) == 3

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "canonical '.toetra' extension" in captured.err


@pytest.mark.parametrize("role", ["model", "dataset"])
def test_output_cannot_overwrite_consumed_artifact(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    role: str,
) -> None:
    specification_path, model_path, dataset_path = _artifacts(tmp_path)
    output = model_path if role == "model" else dataset_path
    original = output.read_bytes()

    assert (
        main(
            [
                "validate",
                str(specification_path),
                "--dataset",
                str(dataset_path),
                "--level",
                "executable",
                "--output",
                str(output),
            ]
        )
        == EXIT_USAGE
    )

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "collides with a consumed input" in captured.err
    assert output.read_bytes() == original


def test_syntax_output_cannot_overwrite_explicit_unconsumed_model(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    specification_path = tmp_path / "policy.toetra"
    model_path = tmp_path / "model.joblib"
    specification_path.write_text(_SOURCE, encoding="utf-8")
    model_path.write_bytes(b"local model placeholder")

    assert (
        main(
            [
                "validate",
                str(specification_path),
                "--level",
                "syntax",
                "--model",
                str(model_path),
                "--output",
                str(model_path),
            ]
        )
        == EXIT_USAGE
    )

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "collides with a consumed input" in captured.err
    assert model_path.read_bytes() == b"local model placeholder"


def test_executable_validation_translation_failure_is_primary_json(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    specification_path, _, dataset_path = _artifacts(tmp_path)

    def reject_translation(*_args: object, **_kwargs: object) -> object:
        raise BackendTranslationError("translation rejected for test")

    monkeypatch.setattr(
        "toetra._backends.z3_backend.runner.Z3Runner.translate",
        reject_translation,
    )

    assert (
        main(
            [
                "validate",
                str(specification_path),
                "--dataset",
                str(dataset_path),
                "--format",
                "json",
            ]
        )
        == EXIT_RUNTIME
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["valid"] is False
    assert payload["diagnostics"][0]["code"] == "BACKEND_TRANSLATION_FAILED"
    assert captured.err == ""


def test_output_write_failure_leaves_no_partial_file(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    specification_path = tmp_path / "policy.toetra"
    specification_path.write_text(_SOURCE, encoding="utf-8")
    destination = tmp_path / "existing-directory"
    destination.mkdir()

    assert (
        main(
            [
                "validate",
                str(specification_path),
                "--level",
                "syntax",
                "--output",
                str(destination),
            ]
        )
        == EXIT_RUNTIME
    )

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Failed to write CLI output" in captured.err
    assert destination.is_dir()
    assert not tuple(tmp_path.glob(".existing-directory.*.tmp"))


def test_validate_syntax_does_not_import_backend_specific_z3(
    tmp_path: Path,
) -> None:
    specification_path = tmp_path / "policy.toetra"
    specification_path.write_text(_SOURCE, encoding="utf-8")
    repository_root = Path(__file__).resolve().parents[3]
    script = r"""
import importlib.abc
import json
import sys

class BlockZ3(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "z3" or fullname.startswith("z3."):
            raise ModuleNotFoundError("z3 import blocked during syntax validation")
        return None

sys.meta_path.insert(0, BlockZ3())
from toetra._cli.main import main
status = main([
    "validate",
    sys.argv[1],
    "--level",
    "syntax",
    "--format",
    "json",
])
assert not any(
    name == "z3" or name.startswith("z3.") for name in sys.modules
)
raise SystemExit(status)
"""
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join(
        (str(repository_root / "src"), str(repository_root))
    )

    result = subprocess.run(
        [sys.executable, "-c", script, str(specification_path)],
        cwd=repository_root,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == EXIT_OK, result.stderr
    payload = json.loads(result.stdout)
    assert payload["valid"] is True
    assert payload["completed_level"] == "syntax"
    assert result.stderr == ""
