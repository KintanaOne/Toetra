from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from toetra._cli.main import EXIT_INCONCLUSIVE, EXIT_OK, EXIT_RUNTIME, EXIT_USAGE, main


def _paths(tmp_path: Path) -> tuple[Path, Path, Path]:
    report = tmp_path / "verification.json"
    specification = tmp_path / "policy.toetra"
    model = tmp_path / "model.joblib"
    report.write_text("{}", encoding="utf-8")
    specification.write_text("target := score", encoding="utf-8")
    model.write_bytes(b"model")
    return report, specification, model


def _result(tmp_path: Path, *, exit_code: int = EXIT_OK) -> SimpleNamespace:
    return SimpleNamespace(
        exit_code=exit_code,
        consumed_paths=(),
        to_text=lambda: "replay text",
        to_json=lambda: json.dumps(
            {
                "schema": "toetra.replay-report-collection",
                "schema_version": 1,
            }
        ),
        to_html=lambda: "<!doctype html><title>Replay</title>",
    )


def test_replay_emits_json_and_preserves_property_order(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    report, specification, model = _paths(tmp_path)
    captured: dict[str, Any] = {}

    def replay(*args: object, **kwargs: object) -> SimpleNamespace:
        captured["args"] = args
        captured["kwargs"] = kwargs
        return _result(tmp_path)

    monkeypatch.setattr(
        "toetra._runtime.archived_replay.replay_archived_report",
        replay,
    )

    assert (
        main(
            [
                "replay",
                str(report),
                "--specification",
                str(specification),
                "--model",
                str(model),
                "--property",
                "2",
                "--property",
                "1",
                "--format",
                "json",
            ]
        )
        == EXIT_OK
    )

    output = json.loads(capsys.readouterr().out)
    assert output["schema"] == "toetra.replay-report-collection"
    assert captured["kwargs"]["property_indices"] == (2, 1)
    assert captured["kwargs"]["tolerance"] == 1e-9


def test_replay_writes_primary_output_atomically(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    report, specification, model = _paths(tmp_path)
    output = tmp_path / "nested" / "replay.json"
    monkeypatch.setattr(
        "toetra._runtime.archived_replay.replay_archived_report",
        lambda *args, **kwargs: _result(tmp_path),
    )

    assert (
        main(
            [
                "replay",
                str(report),
                "--specification",
                str(specification),
                "--model",
                str(model),
                "--format",
                "json",
                "--output",
                str(output),
            ]
        )
        == EXIT_OK
    )

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""
    assert json.loads(output.read_text(encoding="utf-8"))["schema_version"] == 1
    assert not tuple(output.parent.glob(".*.tmp"))


def test_replay_preserves_inconclusive_status(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    report, specification, model = _paths(tmp_path)
    monkeypatch.setattr(
        "toetra._runtime.archived_replay.replay_archived_report",
        lambda *args, **kwargs: _result(tmp_path, exit_code=EXIT_INCONCLUSIVE),
    )

    assert (
        main(
            [
                "replay",
                str(report),
                "--specification",
                str(specification),
                "--model",
                str(model),
            ]
        )
        == EXIT_INCONCLUSIVE
    )
    assert capsys.readouterr().out == "replay text\n"


def test_replay_rejects_output_collision_before_reconstruction(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    report, specification, model = _paths(tmp_path)
    called = False

    def replay(*args: object, **kwargs: object) -> SimpleNamespace:
        nonlocal called
        called = True
        return _result(tmp_path)

    monkeypatch.setattr(
        "toetra._runtime.archived_replay.replay_archived_report",
        replay,
    )

    assert (
        main(
            [
                "replay",
                str(report),
                "--specification",
                str(specification),
                "--model",
                str(model),
                "--output",
                str(report),
            ]
        )
        == EXIT_USAGE
    )

    assert called is False
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "collides" in captured.err.lower()


def test_replay_rejects_invalid_report_extension(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _report, specification, model = _paths(tmp_path)
    report = tmp_path / "verification.txt"
    report.write_text("{}", encoding="utf-8")

    assert (
        main(
            [
                "replay",
                str(report),
                "--specification",
                str(specification),
                "--model",
                str(model),
            ]
        )
        == EXIT_USAGE
    )
    assert "JSON file" in capsys.readouterr().err


def test_replay_rejects_non_finite_tolerance(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    report, specification, model = _paths(tmp_path)

    with pytest.raises(SystemExit) as raised:
        main(
            [
                "replay",
                str(report),
                "--specification",
                str(specification),
                "--model",
                str(model),
                "--tolerance",
                "nan",
            ]
        )

    assert raised.value.code == EXIT_USAGE
    assert "finite non-negative" in capsys.readouterr().err


def test_replay_renderer_failure_is_runtime_status(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    report, specification, model = _paths(tmp_path)
    result = _result(tmp_path)
    result.to_json = lambda: object()
    monkeypatch.setattr(
        "toetra._runtime.archived_replay.replay_archived_report",
        lambda *args, **kwargs: result,
    )

    assert (
        main(
            [
                "replay",
                str(report),
                "--specification",
                str(specification),
                "--model",
                str(model),
                "--format",
                "json",
            ]
        )
        == EXIT_RUNTIME
    )
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Failed to render replay output" in captured.err


def test_replay_uses_specification_model_when_override_is_omitted(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    report, specification, _model = _paths(tmp_path)
    captured: dict[str, Any] = {}

    def replay(*args: object, **kwargs: object) -> SimpleNamespace:
        captured["kwargs"] = kwargs
        return _result(tmp_path)

    monkeypatch.setattr(
        "toetra._runtime.archived_replay.replay_archived_report",
        replay,
    )

    assert (
        main(
            [
                "replay",
                str(report),
                "--specification",
                str(specification),
            ]
        )
        == EXIT_OK
    )

    assert captured["kwargs"]["model"] is None
    assert capsys.readouterr().out == "replay text\n"
