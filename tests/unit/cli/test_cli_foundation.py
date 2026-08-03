from __future__ import annotations

import json

import pytest

from toetra._cli.main import EXIT_OK, EXIT_USAGE, main


def test_empty_invocation_prints_command_index(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main([]) == EXIT_OK

    captured = capsys.readouterr()
    assert "validate" in captured.out
    assert "inspect" in captured.out
    assert "verify" in captured.out
    assert "replay" in captured.out
    assert "init" in captured.out
    assert captured.err == ""


def test_help_does_not_emit_diagnostics(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as raised:
        main(["--help"])

    assert raised.value.code == EXIT_OK
    captured = capsys.readouterr()
    assert "usage: toetra" in captured.out
    assert captured.err == ""


@pytest.mark.parametrize("command", ["validate", "inspect", "verify", "replay", "init"])
def test_each_command_has_dedicated_help(
    command: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as raised:
        main([command, "--help"])

    assert raised.value.code == EXIT_OK
    captured = capsys.readouterr()
    assert f"usage: toetra {command}" in captured.out
    assert captured.err == ""


def test_version_uses_distribution_metadata(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr("toetra._cli.main.version", lambda _: "9.8.7")

    with pytest.raises(SystemExit) as raised:
        main(["--version"])

    assert raised.value.code == EXIT_OK
    captured = capsys.readouterr()
    assert captured.out == "toetra 9.8.7\n"
    assert captured.err == ""


def test_invalid_command_uses_reserved_usage_status(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as raised:
        main(["unknown-command"])

    assert raised.value.code == EXIT_USAGE
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "INVALID_ARGUMENTS" not in captured.err
    assert "invalid choice" in captured.err


def test_invalid_command_can_emit_one_json_diagnostic(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as raised:
        main(["--diagnostic-format", "json", "unknown-command"])

    assert raised.value.code == EXIT_USAGE
    captured = capsys.readouterr()
    assert captured.out == ""
    payload = json.loads(captured.err)
    assert payload["schema"] == "toetra.cli-diagnostic"
    assert payload["schema_version"] == 1
    assert payload["category"] == "usage"
    assert payload["code"] == "INVALID_ARGUMENTS"


@pytest.mark.parametrize("command", ["validate", "inspect", "verify", "replay", "init"])
def test_subcommand_errors_preserve_json_diagnostics(
    command: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as raised:
        main(["--diagnostic-format", "json", command, "--unknown-option"])

    assert raised.value.code == EXIT_USAGE
    captured = capsys.readouterr()
    assert captured.out == ""
    payload = json.loads(captured.err)
    assert payload["schema"] == "toetra.cli-diagnostic"
    assert payload["code"] == "INVALID_ARGUMENTS"


@pytest.mark.parametrize("command", ["validate", "inspect", "verify", "replay", "init"])
def test_pending_commands_fail_explicitly(
    command: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main([command]) == EXIT_USAGE

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "not implemented in this build" in captured.err
