from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from toetra._cli.main import (
    EXIT_INCONCLUSIVE,
    EXIT_INTERRUPTED,
    EXIT_LOGICAL_FAILURE,
    EXIT_OK,
    EXIT_RUNTIME,
    EXIT_TERMINATED,
    EXIT_USAGE,
    main,
)


class _FakeSession:
    def __init__(self, specification: Path, *, exit_code: int) -> None:
        self.specification_path = specification.resolve()
        self.model_path = specification.with_name("model.joblib").resolve()
        self.dataset_path = specification.with_name("dataset.csv").resolve()
        self.exit_code = exit_code
        self.reports = (object(),)
        self.execution_context = SimpleNamespace(
            to_dict=lambda: {
                "declared": {
                    "model": "model.joblib",
                    "target": "score",
                    "dataset": None,
                },
                "effective": {
                    "model": "candidate.joblib",
                    "target": "risk_score",
                    "dataset": "dataset.csv",
                },
                "overrides": {
                    "model": True,
                    "target": True,
                    "dataset": True,
                },
            }
        )
        self.provenance = SimpleNamespace(
            input_fingerprint="sha256:" + "a" * 64,
            completeness=SimpleNamespace(value="complete"),
            software=SimpleNamespace(
                toetra_version="1.0.0rc3",
                toetra_build_id="git:test",
            ),
        )

    def to_text(self) -> str:
        return "verification result"

    def to_json(self) -> str:
        return json.dumps(
            {
                "schema": "toetra.verification-report-collection",
                "schema_version": 6,
                "report_count": 1,
                "provenance": {},
                "reports": [{}],
            },
            indent=2,
        )

    def to_html(self) -> str:
        return "<!doctype html><html><body>verification result</body></html>"


def _specification(tmp_path: Path) -> Path:
    path = tmp_path / "policy.toetra"
    path.write_text('model := "model.joblib"\ntarget := score\n', encoding="utf-8")
    path.with_name("model.joblib").write_bytes(b"model")
    path.with_name("dataset.csv").write_text("a,score\n0,0\n", encoding="utf-8")
    return path


def _install_session(
    monkeypatch: pytest.MonkeyPatch,
    specification: Path,
    *,
    exit_code: int,
) -> _FakeSession:
    session = _FakeSession(specification, exit_code=exit_code)

    def fake_verify(*_args: Any, **_kwargs: Any) -> _FakeSession:
        return session

    monkeypatch.setattr("toetra._cli.commands._verify_request", fake_verify)
    return session


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (EXIT_OK, EXIT_OK),
        (EXIT_LOGICAL_FAILURE, EXIT_LOGICAL_FAILURE),
        (EXIT_INCONCLUSIVE, EXIT_INCONCLUSIVE),
    ],
)
def test_verify_preserves_logical_status_and_json_stdout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    status: int,
    expected: int,
) -> None:
    specification = _specification(tmp_path)
    _install_session(monkeypatch, specification, exit_code=status)

    assert main(["verify", str(specification), "--format", "json"]) == expected

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["schema"] == "toetra.verification-report-collection"
    assert payload["schema_version"] == 6
    assert captured.err == ""


def test_verify_writes_html_primary_output_atomically(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    specification = _specification(tmp_path)
    _install_session(monkeypatch, specification, exit_code=EXIT_OK)
    output = tmp_path / "nested" / "report.html"

    assert (
        main(
            [
                "verify",
                str(specification),
                "--format",
                "html",
                "--output",
                str(output),
            ]
        )
        == EXIT_OK
    )

    captured = capsys.readouterr()
    assert output.read_text(encoding="utf-8").startswith("<!doctype html>")
    assert captured.out == ""
    assert captured.err == ""
    assert not tuple(output.parent.glob(".*.tmp"))


def test_verify_artifact_manifest_is_committed_last_with_matching_hashes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    specification = _specification(tmp_path)
    from toetra._cli import artifacts as artifact_module

    writes: list[Path] = []
    original_write = artifact_module.write_atomic_text

    def tracked_write(*args: Any, **kwargs: Any) -> Path:
        written = original_write(*args, **kwargs)
        writes.append(written)
        return written

    monkeypatch.setattr(artifact_module, "write_atomic_text", tracked_write)
    _install_session(monkeypatch, specification, exit_code=EXIT_LOGICAL_FAILURE)
    artifact_directory = tmp_path / "artifacts"

    assert (
        main(
            [
                "verify",
                str(specification),
                "--format",
                "text",
                "--artifacts-dir",
                str(artifact_directory),
                "--artifact-stem",
                "regression-check",
            ]
        )
        == EXIT_LOGICAL_FAILURE
    )

    captured = capsys.readouterr()
    assert captured.out == "verification result\n"
    assert captured.err == ""
    json_path = artifact_directory / "regression-check.json"
    html_path = artifact_directory / "regression-check.html"
    manifest_path = artifact_directory / "regression-check.manifest.json"
    assert json_path.is_file()
    assert html_path.is_file()
    assert manifest_path.is_file()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert set(manifest) == {
        "schema",
        "schema_version",
        "command",
        "process_status",
        "started_at_utc",
        "completed_at_utc",
        "duration_ms",
        "primary_output",
        "execution_context",
        "verification",
        "artifacts",
        "software",
    }
    assert manifest["schema"] == "toetra.run-manifest"
    assert manifest["schema_version"] == 1
    assert manifest["command"] == "verify"
    assert manifest["process_status"] == EXIT_LOGICAL_FAILURE
    assert manifest["started_at_utc"].endswith("Z")
    assert manifest["completed_at_utc"].endswith("Z")
    assert manifest["duration_ms"] >= 0.0
    assert manifest["primary_output"] == {
        "format": "text",
        "destination": "stdout",
        "path": None,
    }
    assert manifest["execution_context"]["declared"]["target"] == "score"
    assert manifest["execution_context"]["effective"]["target"] == "risk_score"
    assert manifest["execution_context"]["overrides"]["target"] is True
    assert manifest["software"] == {
        "toetra_version": "1.0.0rc3",
        "toetra_build_id": "git:test",
    }
    assert manifest["verification"] == {
        "schema": "toetra.verification-report-collection",
        "schema_version": 6,
        "report_count": 1,
        "input_fingerprint": "sha256:" + "a" * 64,
        "provenance_completeness": "complete",
    }
    assert set(manifest["primary_output"]) == {"format", "destination", "path"}
    assert set(manifest["verification"]) == {
        "schema",
        "schema_version",
        "report_count",
        "input_fingerprint",
        "provenance_completeness",
    }
    assert set(manifest["software"]) == {"toetra_version", "toetra_build_id"}
    assert set(manifest["artifacts"]) == {"json", "html"}
    for role, path in (("json", json_path), ("html", html_path)):
        content = path.read_bytes()
        assert set(manifest["artifacts"][role]) == {
            "path",
            "sha256",
            "size_bytes",
        }
        assert manifest["artifacts"][role]["path"] == path.name
        assert (
            manifest["artifacts"][role]["sha256"] == hashlib.sha256(content).hexdigest()
        )
        assert manifest["artifacts"][role]["size_bytes"] == len(content)
    assert writes[-1] == manifest_path.resolve()
    assert not tuple(artifact_directory.glob(".*.tmp"))


def test_verify_rejects_artifact_stem_without_directory_before_execution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    specification = _specification(tmp_path)

    def must_not_run(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("verification must not start")

    monkeypatch.setattr("toetra._cli.commands._verify_request", must_not_run)

    assert (
        main(
            [
                "verify",
                str(specification),
                "--artifact-stem",
                "report",
            ]
        )
        == EXIT_USAGE
    )

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "requires --artifacts-dir" in captured.err


@pytest.mark.parametrize(
    "stem",
    ["../report", ".", "report name", "-report", "CON", "report."],
)
def test_verify_rejects_non_portable_artifact_stem_before_execution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    stem: str,
) -> None:
    specification = _specification(tmp_path)

    def must_not_run(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("verification must not start")

    monkeypatch.setattr("toetra._cli.commands._verify_request", must_not_run)

    assert (
        main(
            [
                "verify",
                str(specification),
                "--artifacts-dir",
                str(tmp_path / "artifacts"),
                f"--artifact-stem={stem}",
            ]
        )
        == EXIT_USAGE
    )

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "artifact stem" in captured.err.lower()


def test_verify_rejects_primary_output_artifact_collision_without_writes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    specification = _specification(tmp_path)

    def must_not_run(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("verification must not start")

    monkeypatch.setattr("toetra._cli.commands._verify_request", must_not_run)
    artifact_directory = tmp_path / "artifacts"
    output = artifact_directory / "check.json"

    assert (
        main(
            [
                "verify",
                str(specification),
                "--format",
                "json",
                "--output",
                str(output),
                "--artifacts-dir",
                str(artifact_directory),
                "--artifact-stem",
                "check",
            ]
        )
        == EXIT_USAGE
    )

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "collides with another CLI output" in captured.err
    assert not (artifact_directory / "check.manifest.json").exists()
    assert not output.exists()


@pytest.mark.parametrize("role", ["specification", "model", "dataset"])
def test_verify_rejects_explicit_input_output_collision_before_execution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    role: str,
) -> None:
    specification = _specification(tmp_path)
    paths = {
        "specification": specification,
        "model": specification.with_name("model.joblib"),
        "dataset": specification.with_name("dataset.csv"),
    }
    arguments = ["verify", str(specification)]
    if role == "model":
        arguments.extend(["--model", str(paths[role])])
    elif role == "dataset":
        arguments.extend(["--dataset", str(paths[role])])
    arguments.extend(["--output", str(paths[role])])

    def must_not_run(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("verification must not start")

    monkeypatch.setattr("toetra._cli.commands._verify_request", must_not_run)

    assert main(arguments) == EXIT_USAGE
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "collides with a consumed input" in captured.err


def test_verify_artifact_write_failure_returns_runtime_and_no_manifest(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    specification = _specification(tmp_path)
    _install_session(monkeypatch, specification, exit_code=EXIT_OK)
    artifact_directory = tmp_path / "not-a-directory"
    artifact_directory.write_text("occupied", encoding="utf-8")

    assert (
        main(
            [
                "verify",
                str(specification),
                "--artifacts-dir",
                str(artifact_directory),
            ]
        )
        == EXIT_RUNTIME
    )

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Failed to write CLI output" in captured.err
    manifest = artifact_directory.parent / "toetra-verification-report.manifest.json"
    assert not manifest.exists()


def test_verify_propagates_execution_policy_to_shared_runtime(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    specification = _specification(tmp_path)
    session = _FakeSession(specification, exit_code=EXIT_OK)
    captured: dict[str, Any] = {}

    def fake_verify(*_args: Any, **kwargs: Any) -> _FakeSession:
        captured.update(kwargs)
        return session

    monkeypatch.setattr("toetra._cli.commands._verify_request", fake_verify)

    assert (
        main(
            [
                "verify",
                str(specification),
                "--timeout-ms",
                "1250",
                "--max-backend-units",
                "12",
                "--max-memory-mb",
                "256",
                "--seed",
                "7",
            ]
        )
        == EXIT_OK
    )

    policy = captured["execution_policy"]
    assert policy.timeout_ms == 1250
    assert policy.resources.max_backend_units == 12
    assert policy.resources.max_memory_mb == 256
    assert policy.deterministic_seed == 7
    assert capsys.readouterr().err == ""


def test_verify_protects_header_resolved_model_from_primary_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    specification = _specification(tmp_path)
    session = _install_session(monkeypatch, specification, exit_code=EXIT_OK)
    original = session.model_path.read_bytes()

    assert (
        main(
            [
                "verify",
                str(specification),
                "--output",
                str(session.model_path),
            ]
        )
        == EXIT_USAGE
    )

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "collides with a consumed input" in captured.err
    assert session.model_path.read_bytes() == original


def test_verify_primary_output_failure_leaves_artifacts_without_manifest(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    specification = _specification(tmp_path)
    _install_session(monkeypatch, specification, exit_code=EXIT_OK)
    artifact_directory = tmp_path / "artifacts"
    artifact_directory.mkdir()
    stale_manifest = artifact_directory / "check.manifest.json"
    stale_manifest.write_text("stale completion marker", encoding="utf-8")
    output = tmp_path / "occupied-output"
    output.mkdir()

    assert (
        main(
            [
                "verify",
                str(specification),
                "--output",
                str(output),
                "--artifacts-dir",
                str(artifact_directory),
                "--artifact-stem",
                "check",
            ]
        )
        == EXIT_RUNTIME
    )

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Failed to write CLI output" in captured.err
    assert (artifact_directory / "check.json").is_file()
    assert (artifact_directory / "check.html").is_file()
    assert not stale_manifest.exists()


def test_verify_reuses_artifact_rendering_for_matching_primary_format(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    specification = _specification(tmp_path)
    session = _install_session(monkeypatch, specification, exit_code=EXIT_OK)
    calls = {"json": 0, "html": 0}
    original_json = session.to_json
    original_html = session.to_html

    def counted_json() -> str:
        calls["json"] += 1
        return original_json()

    def counted_html() -> str:
        calls["html"] += 1
        return original_html()

    monkeypatch.setattr(session, "to_json", counted_json)
    monkeypatch.setattr(session, "to_html", counted_html)

    assert (
        main(
            [
                "verify",
                str(specification),
                "--format",
                "json",
                "--artifacts-dir",
                str(tmp_path / "artifacts"),
            ]
        )
        == EXIT_OK
    )

    assert calls == {"json": 1, "html": 1}
    assert json.loads(capsys.readouterr().out)["schema_version"] == 6


def test_verify_render_failure_returns_runtime_before_any_output_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    specification = _specification(tmp_path)
    session = _install_session(monkeypatch, specification, exit_code=EXIT_OK)
    artifact_directory = tmp_path / "artifacts"

    def fail_html() -> str:
        raise TypeError("not serializable")

    monkeypatch.setattr(session, "to_html", fail_html)

    assert (
        main(
            [
                "verify",
                str(specification),
                "--artifacts-dir",
                str(artifact_directory),
            ]
        )
        == EXIT_RUNTIME
    )

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Failed to render verification output as html" in captured.err
    assert not artifact_directory.exists()


def test_verify_prevalidates_all_artifact_paths_against_inputs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    specification = _specification(tmp_path)
    _install_session(monkeypatch, specification, exit_code=EXIT_OK)
    artifact_directory = tmp_path / "artifacts"
    dataset = artifact_directory / "check.json"
    artifact_directory.mkdir()
    dataset.write_text("a,score\n0,0\n", encoding="utf-8")
    original = dataset.read_text(encoding="utf-8")

    assert (
        main(
            [
                "verify",
                str(specification),
                "--dataset",
                str(dataset),
                "--artifacts-dir",
                str(artifact_directory),
                "--artifact-stem",
                "check",
            ]
        )
        == EXIT_USAGE
    )

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "collides with a consumed input" in captured.err
    assert dataset.read_text(encoding="utf-8") == original
    assert not (artifact_directory / "check.html").exists()
    assert not (artifact_directory / "check.manifest.json").exists()


def test_verify_manifest_serialization_failure_is_runtime_without_completion_marker(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    specification = _specification(tmp_path)
    _install_session(monkeypatch, specification, exit_code=EXIT_OK)
    artifact_directory = tmp_path / "artifacts"

    def invalid_manifest(*_args: Any, **_kwargs: Any) -> dict[str, object]:
        return {"not_json": object()}

    monkeypatch.setattr(
        "toetra._cli.artifacts.build_run_manifest",
        invalid_manifest,
    )

    assert (
        main(
            [
                "verify",
                str(specification),
                "--artifacts-dir",
                str(artifact_directory),
            ]
        )
        == EXIT_RUNTIME
    )

    captured = capsys.readouterr()
    assert captured.out == "verification result\n"
    assert "Failed to render the CLI run manifest" in captured.err
    assert (artifact_directory / "toetra-verification-report.json").is_file()
    assert (artifact_directory / "toetra-verification-report.html").is_file()
    assert not (
        artifact_directory / "toetra-verification-report.manifest.json"
    ).exists()


def test_verify_interrupt_during_atomic_commit_cleans_temporary_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    specification = _specification(tmp_path)
    _install_session(monkeypatch, specification, exit_code=EXIT_OK)
    output = (tmp_path / "nested" / "report.txt").resolve()
    original_replace = Path.replace

    def interrupt_replace(path: Path, target: str | Path) -> Path:
        if Path(target).resolve() == output:
            raise KeyboardInterrupt
        return original_replace(path, target)

    monkeypatch.setattr(Path, "replace", interrupt_replace)

    assert (
        main(
            [
                "verify",
                str(specification),
                "--output",
                str(output),
            ]
        )
        == EXIT_INTERRUPTED
    )

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "interrupted by the user" in captured.err
    assert not output.exists()
    assert not tuple(output.parent.glob(".*.tmp"))


def test_verify_sigterm_during_atomic_commit_cleans_temporary_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    import toetra._cli.main as cli_main

    specification = _specification(tmp_path)
    _install_session(monkeypatch, specification, exit_code=EXIT_OK)
    output = (tmp_path / "nested" / "report.txt").resolve()
    original_replace = Path.replace

    def terminate_replace(path: Path, target: str | Path) -> Path:
        if Path(target).resolve() == output:
            cli_main._raise_termination(15, None)
        return original_replace(path, target)

    monkeypatch.setattr(Path, "replace", terminate_replace)

    assert (
        main(
            [
                "verify",
                str(specification),
                "--output",
                str(output),
            ]
        )
        == EXIT_TERMINATED
    )

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "terminated by SIGTERM" in captured.err
    assert not output.exists()
    assert not tuple(output.parent.glob(".*.tmp"))


def test_verify_rejects_invalid_json_renderer_output_before_emission(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    specification = _specification(tmp_path)
    session = _install_session(monkeypatch, specification, exit_code=EXIT_OK)

    monkeypatch.setattr(session, "to_json", lambda: "not-json")

    assert (
        main(
            [
                "verify",
                str(specification),
                "--format",
                "json",
            ]
        )
        == EXIT_RUNTIME
    )

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "did not produce valid JSON" in captured.err


def test_verify_help_publishes_formats_artifacts_and_execution_controls(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as raised:
        main(["verify", "--help"])

    assert raised.value.code == EXIT_OK
    captured = capsys.readouterr()
    assert "--format {text,json,html}" in captured.out
    assert "--artifacts-dir DIRECTORY" in captured.out
    assert "--artifact-stem NAME" in captured.out
    assert "--timeout-ms" in captured.out
    assert captured.err == ""
