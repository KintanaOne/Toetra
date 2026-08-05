from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from toetra._cli.main import EXIT_OK, EXIT_USAGE, main


def test_init_prints_only_committed_destination(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    destination = tmp_path / "nested" / "policy.toetra"
    model = tmp_path / "model.joblib"
    model.write_bytes(b"model")
    captured: dict[str, object] = {}

    def initialize(*args: object, **kwargs: object) -> SimpleNamespace:
        captured["args"] = args
        captured["kwargs"] = kwargs
        return SimpleNamespace(destination=destination.resolve())

    monkeypatch.setattr(
        "toetra._runtime.initialization.initialize_specification",
        initialize,
    )

    assert (
        main(
            [
                "init",
                str(destination),
                "--model",
                str(model),
                "--target",
                "score",
                "--force",
            ]
        )
        == EXIT_OK
    )

    output = capsys.readouterr()
    assert output.out == f"{destination.resolve()}\n"
    assert output.err == ""
    assert captured["args"] == (str(destination),)
    assert captured["kwargs"] == {
        "model": str(model),
        "target": "score",
        "dataset": None,
        "force": True,
    }


@pytest.mark.parametrize("missing", ["--model", "--target"])
def test_init_requires_model_and_target_arguments(
    missing: str,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    arguments = ["init", str(tmp_path / "policy.toetra")]
    if missing != "--model":
        arguments.extend(["--model", "model.joblib"])
    if missing != "--target":
        arguments.extend(["--target", "score"])

    with pytest.raises(SystemExit) as raised:
        main(arguments)

    assert raised.value.code == EXIT_USAGE
    captured = capsys.readouterr()
    assert captured.out == ""
    assert missing in captured.err


def test_init_configuration_failure_uses_reserved_status(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    destination = tmp_path / "policy.toetra"
    model = tmp_path / "missing.joblib"

    assert (
        main(
            [
                "init",
                str(destination),
                "--model",
                str(model),
                "--target",
                "score",
            ]
        )
        == EXIT_USAGE
    )

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Serialized model not found" in captured.err
